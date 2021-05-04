import os
import requests
from dotenv import load_dotenv

load_dotenv()

"""
https://discord.com/developers/docs/interactions/slash-commands#registering-a-command
"""
application_id = os.getenv("APP_ID")
server_id = os.getenv("GUILD_ID")
discord_token = os.getenv("DISCORD_TOKEN")

url = f"https://discord.com/api/v8/applications/{application_id}/guilds/{server_id}/commands"

commands = {
    "name": "ServerBoi",
    "description": "Commands to interact with Servers controlled by ServerBoi",
    "options": [
        {
            "name": "Server",
            "description": "What do you want to do?",
            "type": 2,
            "options": [
                {
                    "name": "Start",
                    "type": 1,
                    "description": "Start the specified server.",
                    "options": [
                        {
                            "name": "ID",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True
                        }
                    ]
                },
                {
                    "name": "Stop",
                    "type": 1,
                    "description": "Stop the specified server.",
                    "options": [
                        {
                            "name": "ID",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True
                        }
                    ]
                },
                {
                    "name": "Status",
                    "type": 1,
                    "description": "Get status of the specified server.",
                    "options": [
                        {
                            "name": "ID",
                            "description": "The ID of the server to take action on.",
                            "type": 3,
                            "required": True
                        }
                    ]
                },
                {
                    "name": "List",
                    "type": 1,
                    "description": "Get status of the specified server.",
                },
                {
                    "name": "Add",
                    "type": 1,
                    "description": "Add server to ServerBoi management.",
                    "options": [
                        {
                            "name": "Name",
                            "description": "Name of the server",
                            "type": 3,
                            "required": True
                        },
                        {
                            "name": "Game",
                            "description": "Game that is hosted on the server.",
                            "type": 3,
                            "required": True
                        },
                        {
                            "name": "Service",
                            "description": "The cloud provider the instance is on.",
                            "type": 3,
                            "required": True
                        },
                        {
                            "name": "ServiceIdentifier",
                            "description": "The cloud providers account identifier (AWS: Account ID, Azure: Subscription ID, GCP: Project)",
                            "type": 3,
                            "required": True
                        },
                        {
                            "name": "InstanceId",
                            "description": "The ID of the instance in the cloud provider.",
                            "type": 3,
                            "required": True
                        }
                    ]
                }
            ]
        },
        {
            "name": "Onboard",
            "description": "Onboard your service account to ServerBoi.",
            "type": 2,
            "options": [
                {
                    "name": "AWS",
                    "type": 1,
                    "description": "Onboard AWS Account to ServerBoi."
                }
            ]
        }
    ]
}

headers = {
    "Authorization": f"Bot {discord_token}"
}

if __name__ == "__main__":
    r = requests.post(url, headers=headers, json=commands)
    print(r.content)