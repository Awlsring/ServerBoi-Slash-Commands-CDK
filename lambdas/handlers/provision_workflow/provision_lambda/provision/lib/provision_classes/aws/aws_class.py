# System
import os

# Local
from provision.lib.provision_classes.aws import security_group
from provision.lib.provision_classes.aws import instance
from provision.lib.provision_classes.workflow_class import ProvisionWorkflow
from provision.lib.constants import RETRY, STS, AWS_TABLE

# Boto
from boto3.session import Session
from botocore.exceptions import ClientError


class AWSProvision(ProvisionWorkflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.table = AWS_TABLE
        self.region = kwargs.get("region")

        self.instance_type = kwargs.get(
            "instance",
            self._set_default_instance(),
        )

        user_info = self._get_user_info_from_table(self.table)

        self.account_id = user_info.get("AWSAccountID", None)

        if not self.account_id:
            failure_reason = "No AWS Account is associated with this account."
            self._fail_workflow_status(failure_reason)
            raise Exception(failure_reason)

    def execute(self):
        try:
            assumed_role = STS.assume_role(
                RoleArn=f"arn:aws:iam::{self.account_id}:role/ServerBoi-Resource.Assumed-Role",
                RoleSessionName="ServerBoiValidateAWSAccount",
            )

            session = Session(
                region_name=self.region,
                aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
                aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
                aws_session_token=assumed_role["Credentials"]["SessionToken"],
            )

            ec2_client = session.client("ec2", config=RETRY)
            ec2_resource = session.resource(
                "ec2",
                config=RETRY,
            )

        except ClientError as error:
            print(error)
            failure_reason = f"Unable to assume role in AWS Account {self.account_id}"
            self._fail_workflow_status(failure_reason)
            raise Exception(failure_reason)

        game_data = self.get_build_data()

        ports = game_data["ports"]
        ebs_size = game_data.get("drive_size", 8)

        group_id = security_group.create(ec2_client, self.game, ports)

        if type(group_id) is tuple:
            failure_reason = group_id[1]
            self._fail_workflow_status(failure_reason)
            raise Exception(failure_reason)

        response = instance.create(
            ec2_client,
            ec2_resource,
            group_id,
            self.user_data,
            ebs_size,
            self.instance_type,
        )

        if type(response) is tuple:
            failure_reason = response[1]
            self._fail_workflow_status(failure_reason)
            raise Exception(failure_reason)

        server_info = {
            "instance_id": response.instance_id,
            "port": ports[0],
            "region": self.region,
        }

        return server_info
