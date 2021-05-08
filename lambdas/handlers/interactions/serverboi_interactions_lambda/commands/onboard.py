from flask import request
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError as BotoClientError
import serverboi_interactions_lambda.messages.responses as responses


def route_onboard_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {"aws": onboard_aws, "validate": validate}

    if server_command == "aws":

        account_id = request.json["data"]["options"][0]["options"][0]["options"][0][
            "value"
        ]

        response = server_commands[server_command](account_id)

    elif server_command == "validate":
        service = request.json["data"]["options"][0]["options"][0]["options"][0][
            "value"
        ]
        user_id = request.json["member"]["user"]["id"]

        response = server_commands[server_command](user_id, service)

    return response


def onboard_aws(account_id: str) -> str:
    user_id = request.json["member"]["user"]["id"]
    table = _get_table("ServerBoi-User-List")

    resp = _write_user_info_to_table(user_id, table, AWSAccountID=account_id)

    if resp:

        object_url = "https://serverboi-resources-bucket.s3-us-west-2.amazonaws.com/onboardingCloudformation.json"
        url = f"https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL={object_url}&stackName=ServerlessBoiOnboardingRole"
        message = f"To Onboard your AWS Account: {account_id} to ServerBoi, the proper resources must be created in your AWS Account\n\nUse the following link to perform a One-Click deployment.\n\n{url}"

    else:

        message = "Error adding user account_id to table."

    data = responses.form_response_data(content=message)

    return data


def _get_table(table_name: str) -> boto3.resource:
    dynamo = boto3.resource("dynamodb")
    return dynamo.Table(table_name)


def _get_user_info_from_table(user_id: str, table: boto3.resource) -> str:
    try:
        response = table.query(KeyConditionExpression=Key("UserID").eq(user_id))
    except BotoClientError as error:
        print(error)
        return False

    if len(response["Items"]) != 1:
        print("More than one returned user.")
        return False
    else:
        return response["Items"][0]


def _write_user_info_to_table(user_id: str, table: boto3.resource, **kwargs) -> bool:
    update_expression = "Set"
    expression_attribute_values = {}
    i = 1
    for key, value in kwargs.items():
        update_expression = f"{update_expression} {key} = :val{i},"
        expression_attribute_values[f":val{i}"] = value
        i += 1

    update_expression = update_expression[:-1]

    try:
        response = table.update_item(
            Key={"UserID": user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )
        print(response)
    except BotoClientError as error:
        print(error)
        return False
    return True


def validate(user_id: str, service: str) -> str:
    """
    Assume role into target account to verify account is accessible.
    """
    table = _get_table("ServerBoi-User-List")
    user_info = _get_user_info_from_table(user_id, table)

    account_id = user_info.get("AWSAccountID")

    if account_id:
        sts = boto3.client("sts")
        try:
            sts.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role",
                RoleSessionName="ServerBoiValidateAWSAccount",
            )
        except BotoClientError as error:
            print(error)
            message = "Unable to assume into ServerBoi-Resource.Assumed-Role. Make sure you've created the needed resources in your account."
            data = responses.form_response_data(content=message)
            return data

        message = "Successfully able to access account. You're onboarded!"

    else:
        message = "You have no account registered with ServerBoi. Onboard an account to ServerBoi to get started."

    data = responses.form_response_data(content=message)

    return data
