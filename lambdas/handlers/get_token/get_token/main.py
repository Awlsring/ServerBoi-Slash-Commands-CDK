import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
SQS = boto3.resource("sqs", config=RETRY)
TOKEN_QUEUE = SQS.get_queue_by_name(QueueName=os.environ.get("TOKEN_QUEUE"))
S3 = boto3.resource("s3", config=RETRY)
TOKEN_BUCKET = S3.Bucket(os.environ.get("TOKEN_BUCKET"))


def lambda_handler(event, context):
    try:
        for message in TOKEN_QUEUE.receive_messages():
            execution_name = message.body["Input"]["execution_name"]
            token = message.body["TaskToken"]

            TOKEN_BUCKET.put_object(Body=token, Key=execution_name)

            message.delete()

    except ClientError as error:
        raise error