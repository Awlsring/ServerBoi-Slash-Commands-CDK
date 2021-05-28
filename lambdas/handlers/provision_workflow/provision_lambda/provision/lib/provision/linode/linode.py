import os

# Boto
import boto3
from botocore.config import Config
from linode_api4 import LinodeClient
from provision.lib import utils
from provision.lib.provision.linode.enums import (
    LinodeRegions,
    LinodeInstances,
)

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)

LINODE_TABLE = DYNAMO.Table(os.environ.get("LINODE_TABLE"))


def provision_server(**kwargs) -> dict:
    user_info = utils.get_user_info_from_table(
        kwargs["user_id"],
        LINODE_TABLE,
        kwargs["application_id"],
        kwargs["interaction_token"],
    )

    token = user_info.get("linode_api_key")

    client = LinodeClient(token)

    instance = kwargs.get(
        "instance",
        utils.get_default_instance(kwargs.get("game"), kwargs.get("service")),
    )

    if instance not in LinodeInstances:
        return (False, "Provided instance type not a linode instance type.")

    region = kwargs.get("region")

    if region not in LinodeRegions:
        return (False, "Provided region not a linode region.")

    linode, password = client.linode.instance_create(
        instance, region, image="linode/debian10"
    )

    server_info = {
        "linode_id": linode.id,
        "linode_type": linode.type,
        "linode_password": password,
    }

    return True, server_info
