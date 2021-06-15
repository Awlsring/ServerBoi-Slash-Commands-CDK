import boto3
from botocore.exceptions import ClientError as BotoClientError

from typing import List


def create(ec2_client: boto3.client, game: str, ports: List[str]) -> str:
    group_name = f"ServerBoi-Resource-{game}"
    try:
        creation_response = ec2_client.create_security_group(
            Description=f"Sec group for {game} server.",
            GroupName=group_name,
        )

        group_id = creation_response["GroupId"]

        _set_egress(ec2_client, group_id)

        _set_ingress(ec2_client, group_id, ports)

    except BotoClientError as error:
        print(error)
        if error.response["Error"]["Code"] == "InvalidGroup.Duplicate":
            response = ec2_client.describe_security_groups(
                GroupNames=[
                    group_name,
                ],
            )
            group_id = response["SecurityGroups"][0]["GroupId"]
        else:
            response = "Failed to create security group"
            return (False, response)

    return group_id


def _set_egress(ec2_client: boto3, group_id: str):
    # Allow all outbound
    ec2_client.authorize_security_group_egress(
        GroupId=group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 0,
                "ToPort": 65535,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
            {
                "IpProtocol": "udp",
                "FromPort": 0,
                "ToPort": 65535,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
        ],
    )


def _set_ingress(ec2_client: boto3, group_id: str, ports: List[str]):
    permissions = []

    http = {
        "IpProtocol": "tcp",
        "FromPort": 80,
        "ToPort": 80,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    }

    https = {
        "IpProtocol": "tcp",
        "FromPort": 443,
        "ToPort": 443,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    }

    ssh = {
        "IpProtocol": "tcp",
        "FromPort": 22,
        "ToPort": 22,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
    }

    permissions.append(http)
    permissions.append(https)

    for port in ports:
        tcp = {
            "IpProtocol": "tcp",
            "FromPort": port,
            "ToPort": port,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }
        udp = {
            "IpProtocol": "udp",
            "FromPort": port,
            "ToPort": port,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }

        permissions.append(udp)
        permissions.append(tcp)

    ec2_client.authorize_security_group_ingress(
        GroupId=group_id, IpPermissions=permissions
    )
