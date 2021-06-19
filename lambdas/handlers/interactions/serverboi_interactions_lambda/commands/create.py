from typing import Optional
from flask import request
import boto3
import os
import json
import serverboi_utils.responses as response_utils
import serverboi_utils.embeds as embed_utils
from serverboi_interactions_lambda.enums.aws_enums import AWSRegions, AWSInstanceTypes
from serverboi_interactions_lambda.enums.linode_enums import (
    LinodeRegions,
    LinodeInstanceTypes,
)

from uuid import uuid4
from discord import Color
from serverboi_interactions_lambda.lib.constants import PROVISION_ARN, URL


def route_create_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    create_server_kwargs = {
        "game": server_command,
        "user_id": request.json["member"]["user"]["id"],
        "username": request.json["member"]["user"]["username"],
        "interaction_id": request.json["id"],
        "interaction_token": request.json["token"],
        "application_id": request.json["application_id"],
        "guild_id": request.json["guild_id"],
    }

    options = request.json["data"]["options"][0]["options"][0]["options"]

    for option in options:
        create_server_kwargs[option["name"]] = option["value"]

    return create_server(**create_server_kwargs)


def create_server(**kwargs) -> str:

    service = kwargs.get("service")
    region = kwargs.get("region")
    instance_type = kwargs.get("instance_type")

    incorrect_parameters = verify_input(service, region, instance_type)

    if incorrect_parameters == {}:

        sfn = boto3.client("stepfunctions")

        execution_name = uuid4().hex.upper()

        kwargs["url"] = URL
        kwargs["execution_name"] = execution_name
        input_data = json.dumps(kwargs)

        embed = embed_utils.form_workflow_embed(
            workflow_name=f"Provision-Server",
            workflow_description=f"Workflow ID: {execution_name}",
            status="⏳ Pending",
            stage="Starting...",
            color=Color.greyple(),
        )

        data = response_utils.form_response_data(embeds=[embed])

        sfn.start_execution(
            stateMachineArn=PROVISION_ARN, name=execution_name, input=input_data
        )

    else:
        response = "The following parameters are invalid |"
        for key, value in incorrect_parameters.items():
            response = f"{response} {key}: `{value}` |"
        data = response_utils.form_response_data(content=response)

    return data


def verify_input(service: str, region: str, instance_type: Optional[str]) -> dict:
    incorrect_parameters = {}

    region_enums = {"aws": AWSRegions, "linode": LinodeRegions}
    region_enum = region_enums[service]

    regions = set(item.value for item in region_enum)
    if region not in regions:
        incorrect_parameters["region"] = region
    if instance_type:
        instance_enums = {"aws": AWSInstanceTypes, "linode": LinodeInstanceTypes}
        instance_enum = instance_enums[service]
        instance_types = set(item.value for item in instance_enum)
        if instance_type not in instance_types:
            incorrect_parameters["instance_type"] = instance_type
    return incorrect_parameters