import boto3
from botocore.exceptions import ClientError as BotoClientError

from typing import List


def create(
    ec2_client: boto3.client, game: str, server_id: str, ports: List[str]
) -> str:
    group_name = f"ServerBoi-Resource-{game}-{server_id}"
    try:
        creation_response = ec2_client.create_security_group(
            Description=f"Sec group for {game} server: {server_id}",
            GroupName=group_name,
        )

        group_id = creation_response["GroupId"]

        _set_egress(ec2_client, group_id)

        _set_ingress(ec2_client, group_id, ports)

    except BotoClientError as error:
        print(error)
        raise (error)

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

    for port in ports:
        permission = {
            "IpProtocol": "tcp",
            "FromPort": port,
            "ToPort": port,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }

        permissions.append(permission)

    ec2_client.authorize_security_group_ingress(
        GroupId=group_id, IpPermissions=permissions
    )