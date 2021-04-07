from flask import request
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClietError as BotoClientError


def route_server_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "status": server_status,
        "start": server_start,
        "stop": server_stop,
    }

    server_id = request.json["data"]["options"][0]["options"][0]["options"][0]["value"]

    return server_commands[server_command](server_id)


def server_start(id: int) -> str:
    response = f"Placeholder response for server start. Server {id} was entered"
    instance = _get_resource_from_id(id)

    try:
        instance.start()
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        response = "Instance is starting"
        # Spin off second process to send another message when instance is fully up.

    return response


def server_stop(id: int) -> str:
    response = f"Placeholder response for server stop. Server {id} was entered"
    instance = _get_resource_from_id(id)

    try:
        instance.stop()
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        response = "Instance is stopping"
        # Spin off second process to send another message when instance is fully down.

    return response


def server_status(id: int) -> str:
    response = f"Placeholder response for server status. Server {id} was entered"
    instance = _get_resource_from_id(id)

    try:
        state = instance.state()
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        response = f"Instance is {state['Name']}"

    return response


def _get_server_info_from_table(id: int) -> dict:
    # Set this outside handler
    dynamo = boto3.resource("dynamodb")

    # Use env variable for table name
    server_table = dynamo.Table("ServerlessBoi-Server-List")

    try:
        response = server_table.query(KeyConditionExpression=Key("server_id").eq(id))
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        server_info = response["Items"][0]

    return server_info


def _create_ec2_resource(server_info: dict):
    # Create this sts client in init
    sts_client = boto3.client("sts")

    # Maybe depack all this into a server_info object?
    account_id = server_info.get("account_id")
    instance_id = server_info.get("instance_id")
    region = server_info.get("region")

    try:
        assumed_role_object = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoiRole",
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

    instance = ec2.Instance(instance_id)

    return instance


def _get_resource_from_id(id: int) -> boto3.resource:
    server_info = _get_server_info_from_table(id)
    resource = _create_ec2_resource(server_info)
    return resource