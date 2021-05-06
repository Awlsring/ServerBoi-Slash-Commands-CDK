import boto3
import json
from uuid import uuid4
import os
from botocore.exceptions import ClientError as BotoClientError
from boto3.dynamodb.conditions import Key

DYNAMO = boto3.resource("dynamodb")
USER_TABLE = DYNAMO.Table(os.environ.get("USER_TABLE"))
SERVER_TABLE = DYNAMO.Table(os.environ.get("SERVER_TABLE"))
STS = boto3.client('sts')

# TODO: Find and pull latest Debian
IMAGE_ID = 'ami-0c7ea5497c02abcaf'

def _get_user_info_from_table(user_id: str, table: boto3.resource) -> str:
    try:
        response = USER_TABLE.query(KeyConditionExpression=Key("UserID").eq(user_id))
    except BotoClientError as error:
        print(error)
    
    if len(response["Items"]) != 1:
        raise Exception(f"More than one user with id of {user_id}")
    else:
        return response["Items"][0]

def form_user_data(server_name: str, world_name: str, password: str) -> str:
    return f'''#!/bin/bash
sudo apt-get update && apt-get upgrade -y

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io -y

mkdir -p /valheim-server/config/worlds /valheim-server/data

sudo docker run -d \
    --name valheim-server \
    --cap-add=sys_nice \
    --stop-timeout 120 \
    -p 2456-2457:2456-2457/udp \
    -v /valheim-server/config:/config \
    -v /valheim-server/data:/opt/valheim \
    -e SERVER_NAME="{server_name}" \
    -e WORLD_NAME="{world_name}" \
    -e SERVER_PASS="{password}" \
    lloesche/valheim-server'''

def lambda_handler(event, context) -> dict:
    game = event['game']
    name = event["name"]
    region = event['region']
    user_id = event['user_id']
    password = event['password']
    service = event['service']

    server_id = uuid4()
    server_id = str(server_id)[:4]

    user_info = _get_user_info_from_table(user_id, USER_TABLE)

    account_id = user_info.get("AWSAccountID")
    event['account_id'] = account_id

    if account_id:

        try:
            assumed_role = STS.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/ServerBoi-Resource.Assumed-Role',
                RoleSessionName="ServerBoiValidateAWSAccount"
            )

            # Replace with boto session then creation
            ec2_client = boto3.client(
                "ec2",
                region_name=region,
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken']
            )

            ec2_resource = boto3.resource(
                "ec2",
                region_name=region,
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken']
            )

            print("Account verified")

        except BotoClientError as error:
            print(error)

        with open('verify_and_provision/build.json') as build:
            build_data = json.load(build)

        game_data = build_data[game]

        event['wait_time'] = game_data['build_time']
        port_range = game_data['ports']['range']
        event['server_port'] = game_data['ports']['primary']

        sec_group_name = f"ServerBoi-Resource-{game}-{name}-{server_id}"

        sec_resp = ec2_client.create_security_group(
            Description=f"Sec group for {game} server: {name}",
            GroupName=sec_group_name
        )

        group_id = sec_resp['GroupId']

        ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 0,
                    'ToPort': 65535,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        }
                    ]
                },
                {
                    'IpProtocol': 'udp',
                    'FromPort': 0,
                    'ToPort': 65535,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        }
                    ]
                }
            ]
        )

        ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': port_range[0],
                    'ToPort': port_range[1],
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        }
                    ]
                },
                {
                    'IpProtocol': 'udp',
                    'FromPort': port_range[0],
                    'ToPort': port_range[1],
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        }
                    ]
                },
            ]
        )

        user_data = form_user_data(name, event['world-name'], password)

        instances = ec2_resource.create_instances(
            ImageId=IMAGE_ID,
            InstanceType=game_data['aws']['instance_type'],
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[
                group_id
            ],
            UserData=user_data
        )

        instance = instances[0]

        instance_id = instance.instance_id

        server_item = {
            "ServerID": server_id,
            "Owner": user_id,
            "Game": game,
            "ServerName": name,
            "Password": password,
            "Service": service,
            "AccountID": account_id,
            "Region": region,
            "InstanceID": instance_id
        }

        SERVER_TABLE.put_item(
            Item=server_item
        )

        ip = instance.public_ip_address
        print(f"Instance IP: {ip}")
        
        if ip != '':
            event['instance_ip'] = ip

        event['instance_id'] = instance_id
        
        return event

    else:
        raise Exception("No account associated with user")