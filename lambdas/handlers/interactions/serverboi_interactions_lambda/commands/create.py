from flask import request
from botocore.exceptions import ClientError as BotoClientError
import boto3
import os

PROVISION_ARN = os.environ.get("PROVISION_ARN")

def route_create_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "valheim": create_valheim
    }

    return server_commands[server_command]()

def create_valheim(*args, **kwargs) -> str:
    service = args[0]
    region = args[1]
    name = args[2]
    world_name = args[3]
    password = args[4]
    user_id = args[5]
    game = args[6]
    world_file = kwargs.get("world_file")

    sfn = boto3.client('stepfunctions')

    input_data = {
        "input": {
            "service": service,
            "region": region,
            "name": name,
            "world_name": world_name,
            "password": password,
            "user_id": user_id,
            "game": game
        }
    }

    data = json.dumps(input_data)

    client.start_execution(
        stateMachineArn=PROVISION_ARN,
        input=data
    )

    response = f"Started creation of {game} server. It'll take several minutes for it to be ready."

    return response