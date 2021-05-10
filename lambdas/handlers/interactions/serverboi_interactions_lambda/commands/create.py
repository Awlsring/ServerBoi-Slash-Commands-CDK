from flask import request
from botocore.exceptions import ClientError as BotoClientError
import boto3
import os
import json
import serverboi_interactions_lambda.messages.responses as responses
from uuid import uuid4
from discord import Embed, Color
from time import gmtime, strftime

PROVISION_ARN = os.environ.get("PROVISION_ARN")


def route_create_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {"valheim": create_server}

    create_server_kwargs = {}
    create_server_kwargs["game"] = server_command
    create_server_kwargs["user_id"] = request.json["member"]["user"]["id"]
    create_server_kwargs["user_id"] = request.json["member"]["user"]["username"]

    options = request.json["data"]["options"][0]["options"][0]["options"]

    for option in options:
        create_server_kwargs[option["name"]] = option["value"]

    return server_commands[server_command](**create_server_kwargs)


def create_server(**kwargs) -> str:
    sfn = boto3.client("stepfunctions")

    data = json.dumps(kwargs)

    execution_name = uuid4().hex.upper()

    sfn.start_execution(stateMachineArn=PROVISION_ARN, name=execution_name, input=data)

    embed = form_create_server_embed(data)

    data = responses.form_response_data(embeds=[embed])

    return data

def form_create_server_embed(execution_name: str, data: str) -> Embed:
    wf_name = f"Provision-Server"
    wf_description = f"Workflow ID: {execution_name}"
    parameters = data
    status = "⏳ Pending"
    stage = "Starting..."
    last_updated = f'⏱️ Last updated: {strftime("%H:%M:%S UTC", gmtime())}'

    embed = Embed(
        title=wf_name,
        color=Color.greyple(),
        description=wf_description,
    )

    embed.add_field(name="Parameters", value=parameters, inline=False)
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Stage", value=stage, inline=True)
    embed.set_footer(text=last_updated)

    return embed



