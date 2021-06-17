import os
import boto3
import json
from botocore.exceptions import ClientError
from botocore.config import Config

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)

SFN = boto3.client("stepfunctions", config=RETRY)
S3 = boto3.resource("s3", config=RETRY)
BUCKET_NAME = os.environ.get("TOKEN_BUCKET")
TOKEN_BUCKET = S3.Bucket(BUCKET_NAME)


def lambda_handler(event, context):
    """
    Call stepfunctions and return token from the wait from the bootstrap step
    of Provision Workflow.
    """
    print(event)
    execution_id = event["execution_id"]

    object = S3.Object(BUCKET_NAME, execution_id)
    token = object.get()["Body"].read().decode("utf-8")
    print(token)

    try:
        resp = SFN.send_task_success(
            taskToken=token, output=json.dumps({"status": 200})
        )
        print(resp)
    except ClientError as error:
        print(error)
        raise Exception(error)

    print(resp)

    return event
