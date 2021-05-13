import boto3
from botocore.exceptions import ClientError as BotoClientError

from typing import List


def create(
    ec2_client: boto3.client,
    ec2_resource: boto3.resource,
    group_id: str,
    user_data: str,
    ebs_size: str,
    instance_type: str,
):
    image_id = get_image_id(ec2_client)
    ebs_mapping = form_block_device_mapping(ebs_size)

    instances = ec2_resource.create_instances(
        BlockDeviceMappings=ebs_mapping,
        ImageId=image_id,
        InstanceType=instance_type,
        MaxCount=1,
        MinCount=1,
        SecurityGroupIds=[group_id],
        UserData=user_data,
        KeyName="ServerBoiKey",
    )

    instance = instances[0]

    instance.create_tags(
        Tags=[
            {"Key": "ManagedBy", "Value": "ServerBoi"},
        ]
    )

    return instance


def get_image_id(ec2_client: boto3.client) -> str:
    images = ec2_client.describe_images(
        Filters=[
            {"Name": "description", "Values": ["Debian 10 (20210329-591)"]},
            {"Name": "architecture", "Values": ["x86_64"]},
            {"Name": "virtualization-type", "Values": ["hvm"]},
        ],
        Owners=["136693071363"],
    )

    return images["Images"][0]["ImageId"]


def form_block_device_mapping(ebs_size: int) -> List[dict]:
    return [
        {
            "DeviceName": "/dev/sdh",
            "VirtualName": "ephemeral",
            "Ebs": {
                "DeleteOnTermination": True,
                "VolumeSize": int(ebs_size),
                "VolumeType": "standard",
            },
        },
    ]
