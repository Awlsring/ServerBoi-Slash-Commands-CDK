# System
import os
from typing import Optional

# Boto
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
from botocore.config import Config

# Layers
import requests
from discord import Color, Embed
import serverboi_utils.embeds as embed_utils
import serverboi_utils.responses as response_utils
from serverboi_utils.regions import ServiceRegion

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
STS = boto3.client("sts", config=RETRY)
TOKEN = os.environ.get("DISCORD_TOKEN")

DYNAMO = boto3.resource("dynamodb", config=RETRY)
AWS_TABLE = DYNAMO.Table(os.environ.get("AWS_TABLE"))
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))

WORKFLOW_NAME = "Provision-Server"
STAGE = "Complete Workflow"


def lambda_handler(event, _):
    print(event)
    game = event["game"]
    name = event["name"]
    region = event["region"]
    server_id = event["server_id"]
    service = event["service"]
    guild_id = event["guild_id"]
    interaction_token = event["interaction_token"]
    application_id = event["application_id"]
    execution_name = event["execution_name"]
    port = event["port"]

    # Get instance
    server_info = _get_server_info_from_table(server_id)
    session = _create_session_in_target_account(region, server_info["account_id"])
    ec2 = session.resource("ec2")
    instance = ec2.Instance(server_info["instance_id"])

    # Pull fields from instance
    state = instance.state
    instance_ip = instance.public_ip_address

    # Complete workflow
    wf_embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="✔️ finished",
        stage=STAGE,
        color=Color.dark_green(),
    )
    wf_embed.add_field(name="ServerID", value=server_id, inline=False)

    wf_data = response_utils.form_response_data(embeds=[wf_embed])
    response_utils.edit_response(application_id, interaction_token, wf_data)

    # Post server embed
    service_region = ServiceRegion.generate_from_lookup(region)
    server_embed = embed_utils.form_server_embed(
        server_name=f"{name}",
        server_id=server_id,
        ip=instance_ip,
        port=port,
        status=state["Name"],
        region=service_region,
        game=game,
        owner=server_info["Owner"],
        service=service,
    )
    server_data = response_utils.form_response_data(
        embeds=[server_embed], components="server"
    )
    response_utils.post_new_reponse(application_id, interaction_token, server_data)

    # Post to server page
    _post_to_embeds_channel(server_data, guild_id)

    return {}


def _post_to_embeds_channel(server_data: dict, guild_id: str):
    discord_url = f"https://discord.com/api/v9"
    headers = {"Authorization": f"Bot {TOKEN}"}
    guild_url = f"{discord_url}/guilds/{guild_id}/channels"
    response = requests.get(guild_url, headers=headers)
    channels = response.json()

    for channel in channels:
        if channel["name"] == "serverboi-servers":
            channel_url = f"{discord_url}/channels/{channel['id']}/messages"
            response = requests.post(channel_url, json=server_data, headers=headers)

            print(response.json())


def _create_session_in_target_account(region: str, account_id: str) -> Session:
    try:
        assumed_role = STS.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role",
            RoleSessionName="ServerBoiTerminateFailedInstance",
        )

        session = Session(
            region_name=region,
            aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
            aws_session_token=assumed_role["Credentials"]["SessionToken"],
        )
    except ClientError as error:
        print(error)

    return session


def _get_server_info_from_table(server_id: str) -> Optional[dict]:
    try:
        response = SERVER_TABLE.get_item(Key={"ServerID": server_id})
        print(response)
    except ClientError as error:
        print(error)
        return None

    server_info = response.get("Item", None)
    return server_info