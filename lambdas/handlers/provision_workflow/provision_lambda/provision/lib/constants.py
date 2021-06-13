import os
import boto3
from botocore.config import Config

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)

DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)

USER_TABLE = DYNAMO.Table(os.environ.get("USER_TABLE"))
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))

WORKFLOW_NAME = "Provision-Server"
STAGE = "Provision"

AWS_TABLE = DYNAMO.Table(os.environ.get("AWS_TABLE"))
LINODE_TABLE = DYNAMO.Table(os.environ.get("LINODE_TABLE"))
