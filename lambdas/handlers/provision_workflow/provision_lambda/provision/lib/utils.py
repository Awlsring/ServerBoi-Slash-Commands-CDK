import json

from provision.main import get_fail_embed
from serverboi_utils import responses

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError as BotoClientError


def get_default_instance(game: str, service: str) -> str:
    game_data = get_build_data(game)

    return game_data[service]["instance_type"]


def get_build_data(game: str) -> dict:
    with open("provision/build.json") as build:
        build_data: dict = json.load(build)

    return build_data[game]


def get_user_info_from_table(
    user_id: str, table: boto3.resource, application_id: str, interaction_token: str
) -> dict:
    try:
        response = table.query(KeyConditionExpression=Key("UserID").eq(user_id))
    except BotoClientError as error:
        print(error)

    if len(response["Items"]) > 1:
        embed = get_fail_embed()
        embed.add_field(
            name="Failure",
            value="Multiple users have your name. That is a problem.",
            inline=False,
        )

        data = responses.form_response_data(embeds=[embed])
        responses.edit_response(application_id, interaction_token, data)
    elif len(response["Items"]) == 0:
        embed = get_fail_embed()
        embed.add_field(
            name="Failure", value="You haven't onboarded with ServerBoi", inline=False
        )

        data = responses.form_response_data(embeds=[embed])
        responses.edit_response(application_id, interaction_token, data)

    else:
        return response["Items"][0]
