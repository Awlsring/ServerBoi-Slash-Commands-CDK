from provision.lib.constants import RETRY, LINODE_TABLE
from provision.lib.provision_classes.workflow_class import ProvisionWorkflow

# Boto
import boto3
from botocore.config import Config

from uuid import uuid4
from linode_api4 import LinodeClient

RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)


class LinodeProvision(ProvisionWorkflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.table = LINODE_TABLE
        self.region = kwargs.get("region")

        self.instance = kwargs.get(
            "instance",
            self._set_default_instance(),
        )

        user_info = self._get_user_info_from_table(self.table)

        self.client = LinodeClient(user_info.get("linode_api_key"))

    def execute(self) -> dict:
        image = "linode/debian10"
        label = uuid4()
        images = [image]
        stackscript = self.client.linode.stackscript_create(
            label=label, script=self.user_data, images=images
        )

        linode, password = self.client.linode.instance_create(
            self.instance, self.region, image=image, stackscript=stackscript
        )

        server_info = {
            "linode_id": linode.id,
            "linode_type": linode.type,
            "linode_password": password,
        }

        return server_info