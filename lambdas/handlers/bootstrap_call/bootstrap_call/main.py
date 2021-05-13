import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)

SFN = boto3.client("stepfunctions", config=RETRY)


def lambda_handler(event, context):
    """
    Call stepfunctions and return token from the wait from the bootstrap step
    of Provision Workflow.
    """
    print(event)
    token = event["TaskToken"]
    try:
        resp = (SFN.send_task_success(taskToken=token, output="complete"),)
        print(resp)
    except ClientError as error:
        raise (error)
