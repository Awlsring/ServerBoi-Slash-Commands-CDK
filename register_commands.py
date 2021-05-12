import os
import requests
import dotenv

dotenv.load_dotenv()

"""
https://discord.com/developers/docs/interactions/slash-commands#registering-a-command
"""
application_id = os.environ.get("APP_ID")
server_id = os.environ.get("GUILD_ID")
discord_token = os.environ.get("DISCORD_TOKEN")

url = f"https://discord.com/api/v8/applications/{application_id}/guilds/{server_id}/commands"

print(url)

commands = {
    "name": "sb",
    "description": "Commands to interact with Servers controlled by ServerBoi",
    "options": [
        {
            "name": "server",
            "description": "What do you want to do?",
            "type": 2,
            "options": [
                {
                    "name": "start",
                    "type": 1,
                    "description": "Start the specified server.",
                    "options": [
                        {
                            "name": "id",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True,
                        }
                    ],
                },
                {
                    "name": "stop",
                    "type": 1,
                    "description": "Stop the specified server.",
                    "options": [
                        {
                            "name": "id",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True,
                        }
                    ],
                },
                {
                    "name": "status",
                    "type": 1,
                    "description": "Get status of the specified server.",
                    "options": [
                        {
                            "name": "id",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True,
                        }
                    ],
                },
                {
                    "name": "list",
                    "type": 1,
                    "description": "Get status of the specified server.",
                },
                {
                    "name": "terminate",
                    "type": 1,
                    "description": "Terminate the specified server.",
                    "options": [
                        {
                            "name": "id",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True,
                        }
                    ],
                },
                {
                    "name": "add",
                    "type": 1,
                    "description": "Add server to ServerBoi management.",
                    "options": [
                        {
                            "name": "name",
                            "description": "Name of the server",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "game",
                            "description": "Game that is hosted on the server.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "service",
                            "description": "The cloud provider the instance is on.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "service-identifier",
                            "description": "The cloud providers account identifier (AWS: Account ID, Azure: Subscription ID, GCP: Project)",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "instance-id",
                            "description": "The ID of the instance in the cloud provider.",
                            "type": 3,
                            "required": True,
                        },
                    ],
                },
            ],
        },
        {
            "name": "create",
            "description": "Create a server.",
            "type": 2,
            "options": [
                {
                    "name": "valheim",
                    "type": 1,
                    "description": "Create a Valheim Server.",
                    "options": [
                        {
                            "name": "service",
                            "description": "Service server is hosted on.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "region",
                            "description": "Use ServerBoi generics (US-West) or use a service's specific name (us-west-2)",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "name",
                            "description": "Name of the server.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "world-name",
                            "description": "Name of the servers world.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "password",
                            "description": "Password for server. Must be at least 5 characters in length.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "world-file-url",
                            "description": "Use an existing world file. Must be publicly accessible url.",
                            "type": 3,
                            "required": False,
                        },
                    ],
                },
                {
                    "name": "csgo",
                    "type": 1,
                    "description": "Create a Valheim Server.",
                    "options": [
                        {
                            "name": "service",
                            "description": "Service server is hosted on.",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "region",
                            "description": "Use ServerBoi generics (US-West) or use a service's specific name (us-west-2)",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "name",
                            "description": "Name of the server.",
                            "type": 3,
                            "required": False,
                        },
                    ],
                },
            ],
        },
        {
            "name": "onboard",
            "description": "Onboard your service account to ServerBoi.",
            "type": 2,
            "options": [
                {
                    "name": "aws",
                    "type": 1,
                    "description": "Onboard AWS Account to ServerBoi.",
                    "options": [
                        {
                            "name": "account-id",
                            "description": "ID of the AWS Account to onboard",
                            "type": 3,
                            "required": True,
                        }
                    ],
                },
                {
                    "name": "validate",
                    "type": 1,
                    "description": "Validate cloud account can be reached bn ServerBoi.",
                    "options": [
                        {
                            "name": "service",
                            "description": "Service to validate",
                            "type": 3,
                            "required": True,
                        }
                    ],
                },
            ],
        },
    ],
}

headers = {"Authorization": f"Bot {discord_token}"}

if __name__ == "__main__":
    r = requests.post(url, headers=headers, json=commands)
    print(r.content)