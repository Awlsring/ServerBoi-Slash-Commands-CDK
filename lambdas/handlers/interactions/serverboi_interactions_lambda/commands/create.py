from flask import request
from botocore.exceptions import ClientError as BotoClientError
import boto3
import os
import json
import serverboi_utils.responses as response_utils
import serverboi_utils.embeds as embed_utils
from uuid import uuid4
from discord import Color


PROVISION_ARN = os.environ.get("PROVISION_ARN")
URL = os.environ.get("API_URL")


def route_create_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    create_server_kwargs = {
        "game": server_command,
        "user_id": request.json["member"]["user"]["id"],
        "username": request.json["member"]["user"]["username"],
        "interaction_id": request.json["id"],
        "interaction_token": request.json["token"],
        "application_id": request.json["application_id"],
        "guild_id": request.json["guild_id"],
    }

    options = request.json["data"]["options"][0]["options"][0]["options"]

    for option in options:
        create_server_kwargs[option["name"]] = option["value"]

    return create_server(**create_server_kwargs)


def create_server(**kwargs) -> str:
    sfn = boto3.client("stepfunctions")

    execution_name = uuid4().hex.upper()

    kwargs["url"] = URL
    kwargs["execution_name"] = execution_name
    input_data = json.dumps(kwargs)

    embed = embed_utils.form_workflow_embed(
        workflow_name=f"Provision-Server",
        workflow_description=f"Workflow ID: {execution_name}",
        status="⏳ Pending",
        stage="Starting...",
        color=Color.greyple(),
    )

    data = response_utils.form_response_data(embeds=[embed])

    sfn.start_execution(
        stateMachineArn=PROVISION_ARN, name=execution_name, input=input_data
    )

    return data