import serverboi_utils.embeds as embed_utils
import serverboi_utils.responses as response_utils
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
from discord import Color
import os

DYNAMO = boto3.resource("dynamodb")
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))
STS = boto3.client("sts")

WORKFLOW_NAME = "Provision-Server"
STAGE = "Start Server Client"


def lambda_handler(event, context):
    """
    Rollback all actions done in Provision-Workflow

    Terminate instance
    Delete security group
    Remove server entry from DynamoDB
    """
    region = event["region"]
    server_id = event["server_id"]
    interaction_token = event["interaction_token"]
    application_id = event["application_id"]
    execution_name = event["execution_name"]
    execution_name = event["execution_name"]

    session = _create_session_in_target_account(region, event["account_id"])
    ec2 = session.client("ec2")
    _terminate_instance(ec2, event["instance_id"])

    embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="❌ failed",
        stage=STAGE,
        color=Color.red(),
    )

    SERVER_TABLE.delete_item(Key={"ServerID": server_id})

    data = response_utils.form_response_data(embeds=[embed])
    response_utils.edit_response(application_id, interaction_token, data)


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


def _terminate_instance(ec2: boto3.client, instance_id: str):
    try:
        ec2.terminate_instances(
            InstanceIds=[
                instance_id,
            ],
        )
    except ClientError as error:
        raise error