from flask import request
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError as BotoClientError
from uuid import uuid4


def route_server_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "status": server_status,
        "start": server_start,
        "stop": server_stop,
        "add": add_server,
        "list": server_list
    }

    if server_command == 'list':
        return server_commands[server_command]()
    
    elif server_command == 'add':
        name = request.json["data"]["options"][0]["options"][0]["options"][0]["value"]
        game = request.json["data"]["options"][0]["options"][0]["options"][1]["value"]
        service = request.json["data"]["options"][0]["options"][0]["options"][2]["value"]
        service_id = request.json["data"]["options"][0]["options"][0]["options"][3]["value"]
        instance = request.json["data"]["options"][0]["options"][0]["options"][4]["value"]

        return server_commands[server_command](name, game, service, service_id, instance)

    else:
        server_id = request.json["data"]["options"][0]["options"][0]["options"][0]["value"]

        return server_commands[server_command](server_id)

def server_start(server_id: int) -> str:
    response = f"Placeholder response for server start. Server {server_id} was entered"
    instance = _get_instance_from_id(server_id)

    if not instance:
        return f"{server_id} is not a server."

    try:
        instance.start()
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        response = "Instance is starting"
        # Spin off second process to send another message when instance is fully up.

    return response


def server_stop(server_id: int) -> str:
    response = f"Placeholder response for server stop. Server {server_id} was entered"
    instance = _get_instance_from_id(server_id)

    if not instance:
        return f"{server_id} is not a server."

    try:
        instance.stop()
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        response = "Instance is stopping"
        # Spin off second process to send another message when instance is fully down.

    return response


def server_status(server_id: int) -> str:
    response = f"Placeholder response for server status. Server {server_id} was entered"
    instance = _get_instance_from_id(server_id)

    if not instance:
        return f"{server_id} is not a server."

    try:
        state = instance.state()
    except BotoClientError as error:
        raise RuntimeError(error)
    else:
        response = f"Instance is {state['Name']}"

    return response

def server_list() -> str:
    response = f"**Current managed servers:**\n"

    # Set this outside handler
    dynamo = boto3.resource("dynamodb")

    # Use env variable for table name
    server_table = dynamo.Table("ServerlessBoi-Server-List")

    try:
        table_response = server_table.scan()
    except BotoClientError as error:
        raise RuntimeError(error)

    if len(table_response["Items"]) == 0:
        response = "No servers are currently managed. :("

    else:
        for item in table_response["Items"]:

            server_info = response["Items"][0]

            server_id = server_info.get('ID')
            server_name = server_info.get('Name')
            game = server_info.get('Game')
            account_id = server_info.get('AccountID')
            region = server_info.get('Region')
            instance_id = server_info.get("InstanceID")

            instance = _create_instance_resource(account_id, region, instance_id)

            try:
                state = instance.state()
            except BotoClientError as error:
                raise RuntimeError(error)

            response = f"{response}- ID: {server_id} | Name: {server_name} | Game: {game} | Status: {state['Name']}\n"

    return response


def add_server(name: str, game: str, service: str, service_id: str, region: str, instance: str) -> str:
    # Assume role into account
    if service == 'AWS':
        ec2 = _create_ec2_resource(service_id, instance)
        instance = ec2.Instance(instance)

        # Check server exists   
        try:
            instance.load()
        except BotoClientError as error:
            return f'"{Instance}" is not a valid instance. Server not added.'

        server_item = {
            'Service': service,
            'AccountID': service_id,
            'Region': region,
            'InstanceID': instance
        }

    long_id = uuid4()
    short_id = str(long_id)[:4]

    item.update({
        'ID': short_id,
        'Name': name,
        'Game': game,
    })

    dynamo = boto3.resource('dynamodb')

    table = dynamo.Table(SERVER_TABLE)

    table.put_item(
        Item=server_item
    )

    response = f'Added {name} to management list with the ID: {short_id}.'

    return response

def _get_server_info_from_table(server_id: int) -> dict:
    # Set this outside handler
    dynamo = boto3.resource("dynamodb")

    # Use env variable for table name
    server_table = dynamo.Table("ServerlessBoi-Server-List")

    try:
        response = server_table.query(KeyConditionExpression=Key("server_id").eq(server_id))
    except BotoClientError as error:
        raise RuntimeError(error)
    else:

    if len(response["Items"]) != 1:
        return False
    else:
        return response["Items"][0]

def _create_ec2_resource(account_id: str, region: str):
    # Create this sts client in init
    sts_client = boto3.client("sts")

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

    return ec2


def _get_instance_from_id(server_id: int) -> boto3.resource:

    server_info = _get_server_info_from_table(server_id)

    if not server_info:
        return False

    account_id = server_info.get('AccountID')
    region = server_info.get('Region')
    instance_id = server_info.get("InstanceID")

    instance = _create_instance_resource(account_id, region, instance_id)
    
    return instance

def _create_instance_resource(account_id: str, region: str, instance_id: str) -> boto3.resource:
    
    resource = _create_ec2_resource(account_id, region)

    instance = resource.Instance(instance_id)

    return instance
