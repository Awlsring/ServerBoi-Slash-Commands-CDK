# System
import json
from uuid import uuid4

# Layers
import serverboi_utils.embeds as embed_utils
import serverboi_utils.responses as response_utils
import provision.lib.docker_game_commands as docker
from discord import Color, Embed

# Boto
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


class ProvisionWorkflow(object):
    def __init__(self, **kwargs) -> None:
        self.workflow_name = "Provision-Server"
        self.stage = "Provision"
        self.user_id = kwargs["user_id"]
        self.service = kwargs.get("service")
        self.game = kwargs.get("game")
        self.interaction_token = kwargs.get("interaction_token")
        self.application_id = kwargs.get("application_id")
        self.execution_name = kwargs.get("execution_name")
        self.user_id = kwargs.get("user_id")

        docker_command = docker.route_docker_command(**kwargs)
        print(docker_command)
        self.user_data = docker.form_user_data(docker_command)

        self._update_workflow_status()

    @staticmethod
    def _generate_server_id() -> str:
        server_id = uuid4()
        server_id = str(server_id)[:4].upper()
        return server_id

    def _update_workflow_status(self):
        embed = embed_utils.form_workflow_embed(
            workflow_name=self.workflow_name,
            workflow_description=f"Workflow ID: {self.execution_name}",
            status="🟢 running",
            stage=self.stage,
            color=Color.green(),
        )

        data = response_utils.form_response_data(embeds=[embed])
        response_utils.edit_response(self.application_id, self.interaction_token, data)

    def _get_fail_embed(self) -> Embed:
        return embed_utils.form_workflow_embed(
            workflow_name=self.workflow_name,
            workflow_description=f"Workflow ID: {self.execution_name}",
            status="❌ failed",
            stage=self.stage,
            color=Color.red(),
        )

    def _fail_workflow_status(self, failure_reason: str):
        embed = self._get_fail_embed()
        embed.add_field(
            name="Failure",
            value=failure_reason,
            inline=False,
        )

        data = response_utils.form_response_data(embeds=[embed])
        response_utils.edit_response(self.application_id, self.interaction_token, data)

    def _get_user_info_from_table(self, table: boto3.resource) -> dict:
        try:
            response = table.query(
                KeyConditionExpression=Key("UserID").eq(self.user_id)
            )
        except ClientError as error:
            print(error)

        if len(response["Items"]) > 1:
            failure_reason = "Multiple users have your name. That is a problem."
            self._fail_workflow_status(failure_reason)

        elif len(response["Items"]) == 0:
            failure_reason = ("You haven't onboarded with ServerBoi",)
            self._fail_workflow_status(failure_reason)

        else:
            return response["Items"][0]

    def _set_default_instance(self) -> str:
        game_data = self.get_build_data()

        return game_data[self.service]["instance_type"]

    def get_build_data(self) -> dict:
        with open("provision/build.json") as build:
            build_data: dict = json.load(build)

        return build_data[self.game]