# TODO: Convert to Class

# # System
# import os
# import json

# # Local
# import provision.main as main


# # Boto
# import boto3
# from botocore.config import Config
# from boto3.session import Session
# from boto3.dynamodb.conditions import Key
# from botocore.exceptions import ClientError as BotoClientError


# RETRY = Config(
#     retries={"max_attempts": 10, "mode": "standard"},
# )
# DYNAMO = boto3.resource("dynamodb", config=RETRY)
# STS = boto3.client("sts", config=RETRY)

# GCP_TABLE = DYNAMO.Table(os.environ.get("GCP_TABLE"))


# def provision_server(**kwargs) -> dict:
#     server_info = {}

#     user_id = kwargs.get("user_id")
#     application_id = kwargs.get("application_id")
#     interaction_token = kwargs.get("interaction_token")

#     user_info = main.get_user_info_from_table(
#         user_id, GCP_TABLE, application_id, interaction_token
#     )
