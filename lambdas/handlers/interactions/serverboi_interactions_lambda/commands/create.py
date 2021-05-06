from flask import request
from botocore.exceptions import ClientError as BotoClientError
import boto3
import os
import json

PROVISION_ARN = os.environ.get("PROVISION_ARN")

def route_create_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "valheim": create_server
    }

    create_server_kwargs = {}
    create_server_kwargs['game'] = server_command
    create_server_kwargs['user_id'] = request.json['member']['user']['id']

    options = request.json["data"]["options"][0]["options"][0]["options"]

    for option in options:
        create_server_kwargs[option['name']] = option['value']

    return server_commands[server_command](**create_server_kwargs)

def create_server(**kwargs) -> str:
    sfn = boto3.client('stepfunctions')

    data = json.dumps(kwargs)

    sfn.start_execution(
        stateMachineArn=PROVISION_ARN,
        input=data
    )

    response = f"Started creation of {kwargs.get('game')} server. It'll take several minutes for it to be ready."

    return response