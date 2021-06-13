from flask import request
import boto3
from botocore.exceptions import ClientError as BotoClientError
from uuid import uuid4
import serverboi_utils.responses as response_utils
import serverboi_utils.embeds as embed_utils
from serverboi_utils.regions import ServiceRegion
import os
import json
from typing import Optional
from discord import Color
from serverboi_interactions_lambda.lib.constants import SERVER_TABLE, TERMINATE_ARN, STS


def route_server_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "status": server_status,
        "start": server_start,
        "stop": server_stop,
        "add": add_server,
        "list": server_list,
        "terminate": server_terminate,
    }

    command_kwargs = {
        "interaction_token": request.json["token"],
        "interaction_id": request.json["id"],
        "application_id": request.json["application_id"],
    }

    options = request.json["data"]["options"][0]["options"][0]["options"]

    for option in options:
        command_kwargs[option["name"]] = option["value"]

    return server_commands[server_command](**command_kwargs)


def server_terminate(**kwargs: dict) -> str:
    """
    Input:
    interaction_id
    interaction_token
    application_id
    id
    """
    server_id = kwargs.get("id")
    instance = _get_instance_from_id(server_id)

    if not instance:
        return _bad_server_id(server_id)

    sfn = boto3.client("stepfunctions")

    execution_name = uuid4().hex.upper()

    kwargs["execution_name"] = execution_name
    data = json.dumps(kwargs)

    sfn.start_execution(stateMachineArn=TERMINATE_ARN, name=execution_name, input=data)

    parameter_data = kwargs

    key_to_remove = [
        "interaction_id",
        "interaction_token",
        "application_id",
        "execution_name",
    ]
    for key in key_to_remove:
        parameter_data.pop(key)

    embed = embed_utils.form_workflow_embed(
        workflow_name=f"Terminate-Server",
        workflow_description=f"Workflow ID: {execution_name}",
        status="⏳ Pending",
        stage="Starting...",
        color=Color.greyple(),
    )

    data = response_utils.form_response_data(embeds=[embed])

    return data


def server_start(**kwargs: dict) -> str:
    server_id = kwargs.get("id")

    instance = _get_instance_from_id(server_id)

    if not instance:
        return _bad_server_id(server_id)

    try:
        instance.start()
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        data = response_utils.form_response_data(content=content)
    else:
        content = "Instance is starting"
        data = response_utils.form_response_data(content=content)

    return data


def server_stop(**kwargs: dict) -> str:
    server_id = kwargs.get("id")

    instance = _get_instance_from_id(server_id)

    if not instance:
        return _bad_server_id(server_id)

    try:
        instance.stop()
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        data = response_utils.form_response_data(content=content)
    else:
        data = response_utils.form_response_data(content="Instance is stopping")

    return data


def server_status(**kwargs: dict) -> str:
    server_id = kwargs.get("id")

    server_info = _get_server_info_from_table(server_id)

    if not server_info:
        return _bad_server_id(server_id)

    server_id = server_info["ServerID"]
    owner = server_info["Owner"]
    game = server_info["Game"]
    server_name = server_info["ServerName"]
    service = server_info["Service"]
    region = server_info["Region"]
    instance_id = server_info["InstanceID"]
    account_id = server_info["AccountID"]
    port = server_info["Port"]

    service_region = ServiceRegion.generate_from_lookup(region)

    ec2 = _create_ec2_resource(account_id, region)
    instance = ec2.Instance(instance_id)

    try:
        state = instance.state
        ip = instance.public_ip_address
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        data = response_utils.form_response_data(content=content)
    else:
        embed = embed_utils.form_server_embed(
            server_name=f"{server_name} ({server_id})",
            server_id=server_id,
            ip=ip,
            port=port,
            status=state["Name"],
            region=service_region,
            game=game,
            owner=owner,
            service=service,
        )
        data = response_utils.form_response_data(embeds=[embed])

    return data


def server_list(**kwargs: dict) -> str:

    try:
        table_response = SERVER_TABLE.scan()
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        return response_utils.form_response_data(content=content)

    if len(table_response["Items"]) == 0:
        data = response_utils.form_response_data(
            content="No servers are currently managed. 😔"
        )

    else:

        embeds = []

        for server_info in table_response["Items"]:

            server_id = server_info.get("ServerID")
            server_name = server_info.get("ServerName")
            game = server_info.get("Game")
            owner = server_info.get("Owner")
            account_id = server_info.get("AccountID")
            region = server_info.get("Region")
            instance_id = server_info.get("InstanceID")
            port = server_info["Port"]
            service = server_info["Service"]

            if game == "valheim":
                port = port + 1

            instance = _create_instance_resource(account_id, region, instance_id)

            service_region = ServiceRegion.generate_from_lookup(region)

            try:
                state = instance.state
                ip = instance.public_ip_address
            except BotoClientError as error:
                print(error)
                content = "Error contacting EC2."
                return response_utils.form_response_data(content=content)

            embed = embed_utils.form_server_embed(
                server_name=f"{server_name} ({server_id})",
                server_id=server_id,
                ip=ip,
                port=port,
                status=state["Name"],
                region=service_region,
                game=game,
                owner=owner,
                service=service,
            )

            embeds.append(embed)

        data = response_utils.form_response_data(
            content="**Currently managed servers:**", embeds=embeds
        )

    return data


def add_server(**kwargs: dict) -> str:
    name = kwargs.get("name")
    game = kwargs.get("game")
    service = kwargs.get("service")
    service_id = kwargs.get("service-identifier")

    # Assume role into account
    if service == "AWS":
        region = kwargs.get("region", "us-west-2")
        instance = kwargs.get("instance-id", "us-west-2")
        ec2 = _create_ec2_resource(service_id, instance)
        instance = ec2.Instance(instance)

        # Check server exists
        try:
            instance.load()
        except BotoClientError as error:
            print(error)
            return (
                f'"{instance.instance_id}" is not a valid instance. Server not added.'
            )

        server_item = {
            "Service": service,
            "AccountID": service_id,
            "Region": region,
            "InstanceID": instance.instance_id,
        }

    long_id = uuid4()
    short_id = str(long_id)[:4]

    server_item.update(
        {
            "ID": short_id,
            "Name": name,
            "Game": game,
        }
    )

    SERVER_TABLE.put_item(Item=server_item)

    response = f"Added {name} to management list with the ID: {short_id}."

    return response


def _get_server_info_from_table(server_id: str) -> Optional[dict]:
    try:
        response = SERVER_TABLE.get_item(Key={"ServerID": server_id})
        print(response)
    except BotoClientError as error:
        print(error)
        return None

    server_info = response.get("Item", None)
    return server_info


def _create_ec2_resource(account_id: str, region: str):
    try:
        assumed_role_object = STS.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role",
            RoleSessionName="ServerBoiSession",
        )
    except BotoClientError as error:
        raise RuntimeError(error)

    credentials = assumed_role_object["Credentials"]

    ec2 = boto3.resource(
        "ec2",
        region_name=region,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    return ec2


def _get_instance_from_id(server_id: str) -> boto3.resource:

    server_info = _get_server_info_from_table(server_id)

    if not server_info:
        return None

    account_id = server_info.get("AccountID")
    region = server_info.get("Region")
    instance_id = server_info.get("InstanceID")

    instance = _create_instance_resource(account_id, region, instance_id)

    return instance


def _create_instance_resource(
    account_id: str, region: str, instance_id: str
) -> boto3.resource:

    resource = _create_ec2_resource(account_id, region)

    instance = resource.Instance(instance_id)

    return instance


def _bad_server_id(server_id: str) -> dict:
    return response_utils.form_response_data(
        content=f"No server has the ID `{server_id}`"
    )
