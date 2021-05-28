# System
import os
import json
from uuid import uuid4

# Local
import provision.lib.docker_game_commands as docker
from provision.lib import utils

# Azure
import azure.identity as identity
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import NetworkInterface
from azure.mgmt.compute import ComputeManagementClient

# Boto
import boto3
from botocore.config import Config


RETRY = Config(
    retries={"max_attempts": 10, "mode": "standard"},
)
DYNAMO = boto3.resource("dynamodb", config=RETRY)
STS = boto3.client("sts", config=RETRY)

AZURE_TABLE = DYNAMO.Table(os.environ.get("AZURE_TABLE"))


def provision_server(**kwargs) -> dict:
    server_info = {}

    user_id = kwargs["user_id"]
    application_id = kwargs["application_id"]
    interaction_token = kwargs["interaction_token"]
    region = kwargs["region"]

    user_info = utils.get_user_info_from_table(
        user_id, AZURE_TABLE, application_id, interaction_token
    )

    tenant_id = user_info.get("tenant_id")
    client_id = user_info.get("client_id")
    client_secret = user_info.get("client_secret")
    subscription_id = user_info.get("subscription_id")

    credential = identity.ClientSecretCredential(tenant_id, client_id, client_secret)

    vm_size = kwargs.get(
        "instance",
        utils.get_default_instance(kwargs.get("game"), kwargs.get("service")),
    )

    resource_group = f"ServerBoi-Resource-Group-{region}"
    random_tag = str(uuid4())[:4].upper()
    vnet = "serverboi-vnet"
    subnet = "serverboi-subnet"
    ip = f"severboi-ip-{random_tag}"
    nic_name = f"serverboi-nic-{random_tag}"
    vm_name = f"ServerBoi-{random_tag}"
    username = "serverboi"
    # Dumb, add ssh key later
    password = f"Sb!{uuid4().hex}"

    server_info["system_password"] = password
    server_info["vm_name"] = vm_name

    create_resource_group(credential, subscription_id, resource_group, region)

    nic = create_network_resources(
        credential, subscription_id, resource_group, region, ip, subnet, nic_name, vnet
    )

    create_instance(
        credential,
        subscription_id,
        resource_group,
        vm_name,
        vm_size,
        region,
        username,
        password,
        nic,
    )


def create_resource_group(
    credential: identity.ClientSecretCredential,
    subscription_id: str,
    resource_group: str,
    region: str,
):
    resource_client = ResourceManagementClient(credential, subscription_id)

    resource_client.resource_groups.create_or_update(
        resource_group, {"location": region}
    )


def create_network_resources(
    credential: identity.ClientSecretCredential,
    subscription_id: str,
    resource_group: str,
    region: str,
    ip: str,
    subnet: str,
    nic_name: str,
    vnet: str,
) -> NetworkInterface:

    network_client = NetworkManagementClient(credential, subscription_id)

    try:
        poller = network_client.virtual_networks.begin_create_or_update(
            resource_group,
            vnet,
            {
                "location": region,
                "address_space": {"address_prefixes": ["10.0.0.0/16"]},
            },
        )
        vnet_result = poller.result()

        print(
            f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}"
        )

    except:
        print("Virtual network already exists")

    subnet_poller = network_client.subnets.begin_create_or_update(
        resource_group, vnet, subnet, {"address_prefix": "10.0.0.0/24"}
    )

    ip_poller = network_client.public_ip_addresses.begin_create_or_update(
        resource_group,
        ip,
        {
            "location": region,
            "sku": {"name": "Standard"},
            "public_ip_allocation_method": "Static",
            "public_ip_address_version": "IPV4",
        },
    )

    subnet_result = subnet_poller.result()
    ip_address_result = ip_poller.result()

    nic_poller = network_client.network_interfaces.begin_create_or_update(
        resource_group,
        nic_name,
        {
            "location": region,
            "ip_configurations": [
                {
                    "name": f"{ip}-config",
                    "subnet": {"id": subnet_result.id},
                    "public_ip_address": {"id": ip_address_result.id},
                }
            ],
        },
    )

    nic_result = nic_poller.result()

    return nic_result


def create_instance(
    credential: identity.ClientSecretCredential,
    subscription_id: str,
    resource_group: str,
    vm_name: str,
    vm_size: str,
    region: str,
    username: str,
    password: str,
    nic: NetworkInterface,
):
    compute_client = ComputeManagementClient(credential, subscription_id)

    compute_client.virtual_machines.begin_create_or_update(
        resource_group,
        vm_name,
        {
            "location": region,
            "storage_profile": {
                "image_reference": {
                    "publisher": "Debian",
                    "offer": "debian-10",
                    "sku": "10",
                    "version": "latest",
                },
            },
            "hardware_profile": {"vm_size": f"{vm_size}"},
            "os_profile": {
                "computer_name": vm_name,
                "admin_username": username,
                "admin_password": password,
            },
            "network_profile": {
                "network_interfaces": [
                    {
                        "id": nic.id,
                    }
                ]
            },
        },
    )

    print(f"Provisioning virtual machine {vm_name}")