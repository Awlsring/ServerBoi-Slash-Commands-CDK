from re import I
import a2s
import serverboi_utils.embeds as embed_utils
import serverboi_utils.responses as response_utils
import serverboi_utils.states as state_utils
from serverboi_utils.regions import ServiceRegion
import boto3
from botocore.exceptions import ClientError
from discord import Color
import os

DYNAMO = boto3.resource("dynamodb")
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))
STS = boto3.client("sts")

WORKFLOW_NAME = "Provision-Server"
STAGE = "Start Server Client"


"""
Get instance ip, get server port.
Use a2s to query server
if success, complete
if fail, wait another 1 minute. If 10 fails, fail workflow, terminate host
"""


def _create_resource_in_target_account(region: str, account_id: str) -> boto3.resource:
    try:
        assumed_role = STS.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role",
            RoleSessionName="ServerBoiTerminateFailedInstance",
        )

        ec2_resource = boto3.resource(
            "ec2",
            region_name=region,
            aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
            aws_session_token=assumed_role["Credentials"]["SessionToken"],
        )
    except ClientError as error:
        print(error)

    return ec2_resource


def _terminate_instance(ec2: boto3.resource, instance_id: str):
    try:
        ec2.terminate_instances(
            InstanceIds=[
                instance_id,
            ],
        )
    except ClientError as error:
        raise error


def lambda_handler(event, context) -> dict:
    game = event["game"]
    name = event["name"]
    region = event["region"]
    user_id = event["user_id"]
    username = event["username"]
    server_id = event["server_id"]
    service = event["service"]
    instance_id = event["instance_id"]
    interaction_token = event["interaction_token"]
    application_id = event["application_id"]
    execution_name = event["execution_name"]
    execution_name = event["execution_name"]
    instance_ip = event.get("instance_ip", False)
    server_port = int(event.get("server_port")) + 1
    event["rollback"] = False

    embed = embed_utils.form_workflow_embed(
        workflow_name=WORKFLOW_NAME,
        workflow_description=f"Workflow ID: {execution_name}",
        status="🟢 running",
        stage=STAGE,
        color=Color.green(),
    )

    data = response_utils.form_response_data(embeds=[embed])
    response_utils.edit_response(application_id, interaction_token, data)

    if not instance_ip:
        ec2 = _create_resource_in_target_account(region, event["account_id"])
        instance = ec2.Instance(instance_id)

        state = instance.state
        event["state"] = state
        instance_ip = instance.public_ip_address
        event["instance_ip"] = instance_ip

    try:
        info = a2s.info((instance_ip, server_port))
        print(info)
    except Exception as e:
        print(e)
        info = False

    if info:
        event["server_up"] = True
        wf_embed = embed_utils.form_workflow_embed(
            workflow_name=WORKFLOW_NAME,
            workflow_description=f"Workflow ID: {execution_name}",
            status="✔️ finished",
            stage=STAGE,
            color=Color.dark_green(),
        )

        wf_embed.add_field(name="ServerID", value=server_id, inline=False)

        service_region = ServiceRegion.generate_from_lookup(region)

        server_embed = embed_utils.form_server_embed(
            server_name=f"{name} ({server_id})",
            server_id=user_id,
            ip=instance_ip,
            port=server_port,
            status=state["Name"],
            region=service_region,
            game=game,
            owner=username,
            service=service,
        )

        wf_data = response_utils.form_response_data(embeds=[wf_embed])
        server_data = response_utils.form_response_data(embeds=[server_embed])

        response_utils.edit_response(application_id, interaction_token, wf_data)
        response_utils.post_new_reponse(application_id, interaction_token, server_data)

        return event

    else:
        event["wait_time"] = 60
        event["attempt"] = int(event.get("attempt", 0)) + 1

        if event["attempt"] >= 10:
            # Delete instance
            ec2 = _create_resource_in_target_account(region, event["account_id"])
            _terminate_instance(ec2, event["instance_id"])
            event["rollback"] = True
            event.pop("server_up", None)

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

        else:
            event["server_up"] = False

        return event