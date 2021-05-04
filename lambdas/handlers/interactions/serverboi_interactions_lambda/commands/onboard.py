from flask import request

def route_onboard_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "aws": onboard_aws
    }

    return server_commands[server_command]()

def onboard_aws() -> str:
    object_url = 'https://serverboi-resources-bucket.s3-us-west-2.amazonaws.com/onboardingCloudformation.json'
    url = f"https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL={object_url}&stackName=ServerlessBoiOnboardingRole"
    response = f"To Onboard your AWS Account to ServerBoi, the proper resources must be created in your AWS Account\n\nUse the following link to perform a One-Click deployment.\n\n{url}"

    return response