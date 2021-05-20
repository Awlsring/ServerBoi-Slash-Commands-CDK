# AWS
import boto3
from botocore.config import Config
from boto3.session import Session
from boto3.dynamodb.conditions import Key
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
import provision_and_wait_for_docker.lib.docker_game_commands as docker_commands
import provision_and_wait_for_dockelib.security_group as security_group
import provision_and_wait_for_dockelib.instance as instances

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)

DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)

USER_TABLE = DYNAMO.Table(os.environ.get("USER_TABLE"))
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))

WORKFLOW_NAME = "Provision-Server"
STAGE = "Provision"

# TODO: I think I do this a lot, make this part of ServerBoi utils
def _get_user_info_from_table(user_id: str, table: boto3.resource) -> dict:
    try:
        response = USER_TABLE.query(KeyConditionExpression=Key("UserID").eq(user_id))
    except BotoClientError as error:
        print(error)

    if len(response["Items"]) > 1:
        embed = get_fail_embed()
        embed.add_field(
            name="Failure",
            value="Multiple users have your name. That is a problem.",
            inline=False,
        )

        data = response_utils.form_response_data(embeds=[embed])
        response_utils.edit_response(application_id, interaction_token, data)
    elif len(response["Items"]) == 0:
        embed = get_fail_embed()
        embed.add_field(
            name="Failure", value="You haven't onboarded with ServerBoi", inline=False
        )

        data = response_utils.form_response_data(embeds=[embed])
        response_utils.edit_response(application_id, interaction_token, data)

    else:
        return response["Items"][0]


def get_fail_embed() -> Embed:
    embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="❌ failed",
        stage=STAGE,
        color=Color.red(),
    )

    return embed


def form_user_data(docker_command: str) -> str:
    return f"""#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io -y

{docker_command}"""


def lambda_handler(event: dict, context) -> dict:
    global execution_name
    global application_id
    global interaction_token
    game = event["game"]
    name = event["name"]
    region = event["region"]
    user_id = event["user_id"]
    username = event["username"]
    service = event["service"]
    interaction_token = event["interaction_token"]
    application_id = event["application_id"]
    execution_name = event["execution_name"]
    password = event.get("password")

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

    """
    TODO: To to negate slim chnace of dup record, create this then do conditonal put to Dynamo
    If response in Item exists, then create ID again and retry til a unique one has been formed.
    """
    server_id = uuid4()
    server_id = str(server_id)[:4].upper()

    # Add server ID to event
    event["server_id"] = server_id

    user_info = _get_user_info_from_table(user_id, USER_TABLE)

    account_id = user_info.get("AWSAccountID")
    event["account_id"] = account_id

    if account_id:

        try:
            assumed_role = STS.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role",
                RoleSessionName="ServerBoiValidateAWSAccount",
            )

            session = Session(
                region_name=region,
                aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
                aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
                aws_session_token=assumed_role["Credentials"]["SessionToken"],
            )

            ec2_client = session.client("ec2", config=RETRY)
            ec2_resource = session.resource(
                "ec2",
                config=RETRY,
            )

            print("Account verified")

        except BotoClientError as error:
            # TODO: Add function that ends gracefully and updates discord on error
            print(error)
            raise error

        with open("verify_and_provision/build.json") as build:
            build_data: dict = json.load(build)

        game_data: dict = build_data[game]

        event["wait_time"] = game_data["build_time"]
        ports = game_data["ports"]
        event["server_port"] = ports[0]
        ebs_size = game_data.get("drive_size", 8)
        instance_type = game_data[service]["instance_type"]

        group_id = security_group.create(ec2_client, game, server_id, ports)

        docker_command = docker_commands.route_docker_command(**kwargs)
        print(docker_command)
        user_data = form_user_data(docker_command)

        instance = instances.create(
            ec2_client,
            ec2_resource,
            group_id,
            user_data,
            ebs_size,
            instance_type,
        )

        instance_id = instance.instance_id

        server_item = {
            "ServerID": server_id,
            "OwnerID": user_id,
            "Owner": username,
            "Game": game,
            "ServerName": name,
            "Password": password,
            "Service": service,
            "AccountID": account_id,
            "Region": region,
            "InstanceID": instance_id,
            "Port": ports[0],
        }

        SERVER_TABLE.put_item(Item=server_item)

        ip = instance.public_ip_address
        print(f"Instance IP: {ip}")

        if ip is not None:
            event["instance_ip"] = ip

        event["instance_id"] = instance_id

        return event

    else:

        embed = embed_utils.form_workflow_embed(
            workflow_name=WORKFLOW_NAME,
            workflow_description=f"Workflow ID: {execution_name}",
            status="❌ failed",
            stage=STAGE,
            color=Color.red(),
        )

        data = response_utils.form_response_data(embeds=[embed])
        response_utils.edit_response(application_id, interaction_token, data)

        raise Exception("No account associated with user")
