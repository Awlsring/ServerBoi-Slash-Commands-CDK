import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
S3 = boto3.resource("s3", config=RETRY)
TOKEN_BUCKET = S3.Bucket(os.environ.get("TOKEN_BUCKET"))


def lambda_handler(event, context):
    print(event)
    try:
        execution_name = event["Input"]["execution_name"]
        token = event["TaskToken"]

        TOKEN_BUCKET.put_object(Body=token, Key=execution_name)

    except ClientError as error:
        raise error

    return event["Input"]
