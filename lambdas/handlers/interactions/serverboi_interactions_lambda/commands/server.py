from flask import request
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError as BotoClientError
from uuid import uuid4
import serverboi_interactions_lambda.messages.responses as responses
from serverboi_utils.regions import Region, ServiceRegion
import os

SERVER_TABLE = os.environ.get("SERVER_TABLE")


def route_server_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "status": server_status,
        "start": server_start,
        "stop": server_stop,
        "add": add_server,
        "list": server_list,
    }

    if server_command == "list":
        return server_commands[server_command]()

    elif server_command == "add":
        name = request.json["data"]["options"][0]["options"][0]["options"][0]["value"]
        game = request.json["data"]["options"][0]["options"][0]["options"][1]["value"]
        service = request.json["data"]["options"][0]["options"][0]["options"][2][
            "value"
        ]
        service_id = request.json["data"]["options"][0]["options"][0]["options"][3][
            "value"
        ]
        instance = request.json["data"]["options"][0]["options"][0]["options"][4][
            "value"
        ]

        return server_commands[server_command](
            name, game, service, service_id, instance
        )

    else:
        server_id = request.json["data"]["options"][0]["options"][0]["options"][0][
            "value"
        ]

        return server_commands[server_command](server_id)


def server_start(server_id: str) -> str:
    instance = _get_instance_from_id(server_id)

    if not instance:
        content = f"ServerID: {server_id} is not a server."
        data = responses.form_response_data(content=content)

    try:
        instance.start()
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        data = responses.form_response_data(content=content)
    else:
        content = "Instance is starting"
        data = responses.form_response_data(content=content)

    return data


def server_stop(server_id: str) -> str:
    instance = _get_instance_from_id(server_id)

    if not instance:
        return responses.form_response_data(
            content=f"ServerID: {server_id} is not a server."
        )

    try:
        instance.stop()
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        data = responses.form_response_data(content=content)
    else:
        data = responses.form_response_data(content="Instance is stopping")

    return data


def server_status(server_id: str) -> str:
    server_info = _get_server_info_from_table(server_id)

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

    if not server_info:
        return responses.form_response_data(
            content=f"ServerID: {server_id} is not a server."
        )

    ec2 = _create_ec2_resource(account_id, region)
    instance = ec2.Instance(instance_id)

    try:
        state = instance.state
        ip = instance.public_ip_address
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        data = responses.form_response_data(content=content)
    else:
        embed = responses.form_server_embed(
            server_name=server_name,
            server_id=server_id,
            ip=ip,
            port=port,
            status=state["Name"],
            region=service_region,
            game=game,
            owner=owner,
            service=service,
        )
        data = responses.form_response_data(embeds=[embed])

    return data


def server_list() -> str:
    response = f"**Current managed servers:**\n"

    # Set this outside handler
    dynamo = boto3.resource("dynamodb")

    # Use env variable for table name
    server_table = dynamo.Table("ServerBoi-Server-List")

    try:
        table_response = server_table.scan()
    except BotoClientError as error:
        print(error)
        content = "Error contacting EC2."
        return responses.form_response_data(content=content)

    if len(table_response["Items"]) == 0:
        data = responses.form_response_data(
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

            instance = _create_instance_resource(account_id, region, instance_id)

            try:
                state = instance.state
                ip = instance.public_ip_address
            except BotoClientError as error:
                print(error)
                content = "Error contacting EC2."
                return responses.form_response_data(content=content)

            embed = responses.form_server_embed(
                server_name=server_name,
                server_id=server_id,
                ip=ip,
                port=port,
                status=state["Name"],
                location=region,
                game=game,
                owner=owner,
                service=service,
            )

            embeds.append(embed)

        data = responses.form_response_data(
            content="**Currently managed servers:**", embeds=embeds
        )

    return data


def add_server(
    name: str, game: str, service: str, service_id: str, region: str, instance: str
) -> str:
    # Assume role into account
    if service == "AWS":
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

    dynamo = boto3.resource("dynamodb")

    table = dynamo.Table(SERVER_TABLE)

    table.put_item(Item=server_item)

    response = f"Added {name} to management list with the ID: {short_id}."

    return response


def _get_server_info_from_table(server_id: str) -> dict:
    # Set this outside handler
    dynamo = boto3.resource("dynamodb")

    # Use env variable for table name
    server_table = dynamo.Table("ServerBoi-Server-List")

    try:
        response = server_table.get_item(Key={"ServerID": server_id})
        print(response)
    except BotoClientError as error:
        print(error)
        return False
    else:
        return response["Item"]


def _create_ec2_resource(account_id: str, region: str):
    # Create this sts client in init
    sts_client = boto3.client("sts")

    try:
        assumed_role_object = sts_client.assume_role(
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
        return False

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
