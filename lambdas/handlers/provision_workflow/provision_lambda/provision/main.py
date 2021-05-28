import boto3
from botocore.config import Config
from boto3.session import Session
from botocore.exceptions import ClientError as BotoClientError

# System
import os
import json
from uuid import uuid4

# Layers
import serverboi_utils.embeds as embed_utils
import serverboi_utils.responses as response_utils
from discord import Color, Embed

# Local
from provision.lib.provision.aws import aws
import provision.lib.provision.gcp.base as gcp
from provision.lib.provision import azure
from provision.lib.provision.linode import linode


RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)

DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)

USER_TABLE = DYNAMO.Table(os.environ.get("USER_TABLE"))
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))

WORKFLOW_NAME = "Provision-Server"
STAGE = "Provision"


service_providers = {
    "aws": aws.provision_server,
    "azure": azure.provision_server,
    "gcp": gcp.provision_server,
    "linode": linode.provision_server,
}


def lambda_handler(event: dict, _) -> dict:
    global execution_name
    game = event["game"]
    name = event["name"]
    user_id = event["user_id"]
    username = event["username"]
    service = event["service"]
    interaction_token = event["interaction_token"]
    application_id = event["application_id"]
    execution_name = event["execution_name"]
    password = event.get("password", None)

    # pack event into a dict cause lambda flips if you try to **event -_-
    kwargs = {}
    for item, value in event.items():
        kwargs[item] = value

    embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="🟢 running",
        stage=STAGE,
        color=Color.green(),
    )

    data = response_utils.form_response_data(embeds=[embed])
    response_utils.edit_response(application_id, interaction_token, data)

    result, response = service_providers[service](kwargs)

    if result:
        for i in range(0, 10):
            server_id = _generate_server_id()

            server_item = {
                "ServerID": server_id,
                "OwnerID": user_id,
                "Owner": username,
                "Game": game,
                "Name": name,
                "Service": service,
            }

            if password:
                server_item["Password"] = password

            server_item.update(response)
            event["server_id"] = server_id

            try:
                SERVER_TABLE.put_item(Item=server_item)
            except Exception as error:
                if i < 10:
                    continue
                else:
                    raise error

    else:
        embed = embed_utils.form_workflow_embed(
            workflow_name=WORKFLOW_NAME,
            workflow_description=f"Workflow ID: {execution_name}",
            status="❌ failed",
            stage=STAGE,
            color=Color.red(),
        )

        data = response_utils.form_response_data(content=response, embeds=[embed])
        response_utils.edit_response(application_id, interaction_token, data)

        raise Exception("No account associated with user")


def _generate_server_id() -> str:
    server_id = uuid4()
    server_id = str(server_id)[:4].upper()
    return server_id


def get_fail_embed() -> Embed:
    embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="❌ failed",
        stage=STAGE,
        color=Color.red(),
    )

    return embed