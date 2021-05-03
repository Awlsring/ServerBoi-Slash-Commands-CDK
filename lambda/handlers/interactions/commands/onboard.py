def route_onboard_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "aws": onboard_aws
    }

    return server_commands[server_command]()

def onboard_aws() -> str:
    object_url = 'https://serverboi-resources-bucket.s3-us-west-2.amazonaws.com/onboardingCloudformation.json'
    url = f'https://us-east-1.signin.aws.amazon.com/oauth?response_type=code&client_id=arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fcloudformation&redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2Fcloudformation%2Fhome%3Fregion%3Dus-east-1%26state%3DhashArgs%2523%252Fstacks%252Fcreate%252Freview%253FtemplateURL%253D{object_url}%2526stackName%253DEBSDEMO%26isauthcode%3Dtrue&forceMobileLayout=0&forceMobileApp=0&code_challenge=ko4Pf7_1XIjCRWC2hN6tFt45unfO7EiekqXbZWuk0kQ&code_challenge_method=SHA-256'

    response = f"To Onboard your AWS Account to ServerBoi, the proper resources must be created in your AWS Account\n\nUse the following link to perform a One-Click deployment.\n\n{url}"

    return response