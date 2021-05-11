import boto3
import os

from discord import Color

from botocore.exceptions import ClientError as BotoClientError

import serverboi_utils.responses as response_utils
import serverboi_utils.embeds as embed_utils
import serverboi_utils.states as state_utils

DYNAMO = boto3.resource("dynamodb")
STS = boto3.client("sts")
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))

WORKFLOW_NAME = "Terminate-Server"
STAGE = "Terminate and Deregister"


def lambda_handler(event, context) -> dict:
    server_id = event["server_id"]
    interaction_token = event["interaction_token"]
    application_id = event["application_id"]
    execution_name = event["execution_name"]

    # Update embed
    embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="🟢 running",
        stage=STAGE,
        color=Color.green(),
    )

    data = response_utils.form_response_data(embeds=[embed])
    response_utils.edit_response(application_id, interaction_token, data)

    # Pull item
    try:
        response = SERVER_TABLE.get_item(Key={"ServerID": server_id})
        print(response)
    except BotoClientError as error:
        print(error)
        return False

    server_info = response["Item"]

    # Unpack item
    server_id = server_info["ServerID"]
    region = server_info["Region"]
    instance_id = server_info["InstanceID"]
    account_id = server_info["AccountID"]

    try:
        assumed_role = STS.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role",
            RoleSessionName="ServerBoiValidateAWSAccount",
        )

        ec2_resource = boto3.resource(
            "ec2",
            region_name=region,
            aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
            aws_session_token=assumed_role["Credentials"]["SessionToken"],
        )

        print("Account verified")

        instance = ec2_resource.Instance(instance_id)

        instance.terminate()

        SERVER_TABLE.delete_item(Key={"ServerID": server_id})

    except BotoClientError as error:
        print(error)
        embed = embed_utils.form_workflow_embed(
            workflow_name=WORKFLOW_NAME,
            workflow_description=f"Workflow ID: {execution_name}",
            status="❌ failed",
            stage=STAGE,
            color=Color.red(),
        )

        data = response_utils.form_response_data(embeds=[embed])
        response_utils.edit_response(application_id, interaction_token, data)
        raise error

    wf_embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="✔️ finished",
        stage=STAGE,
        color=Color.dark_green(),
    )

    data = response_utils.form_response_data(embeds=[wf_embed])
    response_utils.edit_response(application_id, interaction_token, data)

    return True
