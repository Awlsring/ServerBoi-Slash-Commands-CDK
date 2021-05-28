# System
import os
import json

# Local
from provision.lib import utils
from provision.lib.provision.aws.enums import AWSInstances, AWSRegions
import provision.lib.provision.aws.security_group as security_group
import provision.lib.provision.aws.instance as instances
import provision.lib.docker_game_commands as docker
import provision.main as main
import serverboi_utils.responses as response_utils


# Boto
import boto3
from botocore.config import Config
from boto3.session import Session
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError as BotoClientError

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)

AWS_TABLE = DYNAMO.Table(os.environ.get("AWS_TABLE"))


def provision_server(**kwargs) -> dict:
    server_info = {}

    user_id = kwargs["user_id"]
    application_id = kwargs["application_id"]
    interaction_token = kwargs["interaction_token"]
    game = kwargs["game"]

    user_info = main.get_user_info_from_table(
        user_id, AWS_TABLE, application_id, interaction_token
    )

    account_id = user_info.get("AccountID", None)

    if not account_id:
        return (False, {"No AWS Account is associated with this account."})

    region = kwargs.get("region")

    if region not in AWSRegions:
        return (False, "Provided region not is an AWS region.")

    instance_type = kwargs.get(
        "instance",
        utils.get_default_instance(game, kwargs.get("service")),
    )

    if instance_type not in AWSInstances:
        return (False, "Provided instance type is not an AWS instance type.")

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

    except BotoClientError as error:
        print(error)
        return (False, f"Unable to assume role in AWS Account {account_id}")

    game_data = utils.get_build_data(game)

    ports = game_data["ports"]
    ebs_size = game_data.get("drive_size", 8)

    group_id = security_group.create(ec2_client, game, ports)

    docker_command = docker.route_docker_command(**kwargs)
    print(docker_command)
    user_data = docker.form_user_data(docker_command)

    response = instances.create(
        ec2_client,
        ec2_resource,
        group_id,
        user_data,
        ebs_size,
        instance_type,
    )

    if response is tuple:
        return response

    server_info["instance_id"] = response.instance_id

    return True, server_info