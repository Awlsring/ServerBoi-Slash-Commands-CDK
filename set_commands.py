import os
import requests
import dotenv
from requests.api import options

dotenv.load_dotenv()

"""
https://discord.com/developers/docs/interactions/slash-commands#registering-a-command
"""
application_id = os.environ.get("APP_ID")
server_id = os.environ.get("GUILD_ID")
discord_token = os.environ.get("DISCORD_TOKEN")

url = f"https://discord.com/api/v9/applications/{application_id}/guilds/{server_id}/commands"

print(url)

service_choices = [
    {
        "name": "AWS",
        "value": "aws"
    },
    {
        "name": "Linode",
        "value": "linode"
    }
]

service_blob = {
    "name": "service",
    "description": "Service server is hosted on.",
    "type": 3,
    "required": True,
    "choices": service_choices
}

override_region_blob = {
    "name": "override-region",
    "description": "Overried the selected region for a service specific one",
    "type": 3,
    "required": False,
}

override_hardware_blob = {
    "name": "override-hardware",
    "description": "Override the default hardware for the server",
    "type": 3,
    "required": False,
}

create_profile_blob = {
    "name": "profile",
    "description": "Profile to create server for",
    "type": 8,
    "required": False,
}

private_blob = {
    "name": "private",
    "description": "Defaults to public. If server is private, server won't be listed",
    "type": 5,
    "required": False,
}

profile_blob = {
    "name": "profile",
    "description": "Profile to create server. If not set, will be your personal default",
    "type": 3,
    "required": False,
    "choices": [
        {
            "name": "Personal",
            "value": "aws"
        },
    ]
}

region_blob = {
    "name": "region",
    "description": "Use ServerBoi generics (US-West) or use a service's specific name (us-west-2)",
    "type": 3,
    "required": True,
    "choices": [
        {
            "name": "US-West",
            "value": "us-west"
        },
        {
            "name": "US-East",
            "value": "us-east"
        },
        {
            "name": "US-Central",
            "value": "us-central"
        },
        {
            "name": "US-South",
            "value": "us-south"
        },
        {
            "name": "Override",
            "value": "override"
        }
    ]
}

name_blob = {
    "name": "name",
    "description": "Name of the server.",
    "type": 3,
    "required": False,
}

server_id_blob = {
    "name": "id",
    "description": "The ID of the server to take action on.",
    "type": 3,
    "required": True,
}

create_commands = {
    "name": "create",
    "description": "Create a server.",
    "type": 1,
    "options": [
        {
            "name": "valheim",
            "type": 1,
            "description": "Create a Valheim server.",
            "options": [
                service_blob,
                region_blob,
                create_profile_blob,
                private_blob,
                name_blob,
                {
                    "name": "world-name",
                    "description": "Name of the servers world.",
                    "type": 3,
                    "required": False,
                },
                {
                    "name": "password",
                    "description": "Password for server. Must be at least 6 characters in length. Defaults to `secret`",
                    "type": 3,
                    "required": False,
                },
                {
                    "name": "server-public",
                    "description": "If the server should be publicly listed on steam.",
                    "type": 5,
                    "required": False,
                },
                override_region_blob,
                override_hardware_blob
            ],
        },
        {
            "name": "csgo",
            "type": 1,
            "description": "Create a CSGO server.",
            "options": [
                service_blob,
                region_blob,
                {
                    "name": "gsl-token",
                    "description": "REQUIRED for listing server. Create with Steam account at tinyurl.com/3afvzmd5",
                    "type": 3,
                    "required": True,
                },
                create_profile_blob,
                private_blob,
                name_blob,
                override_region_blob,
                override_hardware_blob
            ],
        },
        {
            "name": "ns2",
            "type": 1,
            "description": "Create a Natural Selection 2 server.",
            "options": [
                service_blob,
                region_blob,
                create_profile_blob,
                private_blob,
                name_blob,
                override_region_blob,
                override_hardware_blob
            ],
        },
        {
            "name": "wg",
            "type": 1,
            "description": "Create a Wireguard server.",
            "options": [
                service_blob,
                region_blob,
                create_profile_blob,
                private_blob,
                name_blob,
                override_region_blob,
                override_hardware_blob
            ],
        },
    ],
}

server_commands = {
    "name": "server",
    "description": "What do you want to do?",
    "type": 1,
    "options": [
        {
            "name": "start",
            "type": 1,
            "description": "Start the specified server.",
            "options": [
                server_id_blob
            ],
        },
        {
            "name": "stop",
            "type": 1,
            "description": "Stop the specified server.",
            "options": [
                server_id_blob
            ],
        },
        {
            "name": "reboot",
            "type": 1,
            "description": "Reboot the specified server.",
            "options": [
                server_id_blob
            ],
        },
        {
            "name": "status",
            "type": 1,
            "description": "Get status of the specified server.",
            "options": [
                server_id_blob
            ],
        },
        {
            "name": "relist",
            "type": 1,
            "description": "Relist server embed if it was removed.",
            "options": [
                server_id_blob
            ],
        },
        {
            "name": "ssh-key",
            "type": 1,
            "description": "Retrieve ssh key for server.",
            "options": [
                server_id_blob
            ],
        },
        {
            "name": "terminate",
            "type": 1,
            "description": "Terminate the specified server.",
            "options": [
                server_id_blob
            ],
        },
    ],
}

deauthorize_commands = {
    "name": "deauthorize",
    "description": "Deauthorize user or role for server actions",
    "type": 1,
    "options": [
        {
            "name": "user",
            "description": "Authorize a user to perform server actions on a specified server.",
            "type": 1,
            "options": [
                server_id_blob,
                {
                    "name": "user",
                    "description": "User to authorize",
                    "type": 6,
                    "required": True,
                },
            ]
        },
        {
            "name": "role",
            "description": "Authorize a role to perform server actions on a specified server.",
            "type": 1,
            "options": [
                server_id_blob,
                {
                    "name": "role",
                    "description": "Role to authorize",
                    "type": 8,
                    "required": True,
                }
            ]
        }
    ]
}

authorize_commands = {
    "name": "authorize",
    "description": "Authorize user or role for server actions",
    "type": 1,
    "options": [
        {
            "name": "user",
            "description": "Authorize a user to perform server actions on a specified server.",
            "type": 1,
            "options": [
                server_id_blob,
                {
                    "name": "user",
                    "description": "User to authorize",
                    "type": 6,
                    "required": True,
                },
            ]
        },
        {
            "name": "role",
            "description": "Authorize a role to perform server actions on a specified server.",
            "type": 1,
            "options": [
                server_id_blob,
                {
                    "name": "role",
                    "description": "Role to authorize",
                    "type": 8,
                    "required": True,
                }
            ]
        }
    ]
}


remove_commands = {
    "name": "remove",
    "description": "Remove account.",
    "type": 1,
    "options": [
        {
            "name": "personal",
            "type": 1,
            "description": "Remove personal account.",
            "options": [
                {
                    "name": "service",
                    "description": "Service to remove.",
                    "type": 3,
                    "required": True,
                    "choices": service_choices
                }
            ]    
        },
        {
            "name": "profile",
            "type": 1,
            "description": "Remove account from profile.",
            "options": [
                {
                    "name": "service",
                    "description": "Service to remove.",
                    "type": 3,
                    "required": True,
                    "choices": service_choices
                },
                {
                    "name": "role",
                    "description": "Role of profile.",
                    "type": 8,
                    "required": True,
                }
            ]    
        },
    ],
}


set_commands = {
    "name": "set",
    "description": "Set account for profile.",
    "type": 1,
    "options": [
        {
            "name": "personal",
            "type": 2,
            "description": "Add account to personal profile.",
            "options": [
                {
                    "name": "aws",
                    "description": "Add AWS account to personal profile",
                    "type": 1,
                    "options": [
                        {
                            "name": "account-id",
                            "description": "ID of the AWS Account to add",
                            "type": 3,
                            "required": True,
                        },
                    ]
                },
                {
                    "name": "linode",
                    "type": 1,
                    "description": "Add Linode account to personal profile.",
                    "options": [
                        {
                            "name": "api-key",
                            "description": "Api Key for Linode account to add",
                            "type": 3,
                            "required": True,
                        },
                    ],
                },
            ],
        },
        {
            "name": "profile",
            "type": 2,
            "description": "Add account to Profile.",
            "options": [
                {
                    "name": "aws",
                    "description": "Add AWS account to Profile",
                    "type": 1,
                    "options": [
                        {
                            "name": "account-id",
                            "description": "ID of the AWS Account to add",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "role",
                            "description": "Role of the profile",
                            "type": 8,
                            "required": True,
                        },
                    ]
                },
                {
                    "name": "linode",
                    "type": 1,
                    "description": "Add Linode account to Profile.",
                    "options": [
                        {
                            "name": "api-key",
                            "description": "Api Key for Linode account to add",
                            "type": 3,
                            "required": True,
                        },
                        {
                            "name": "role",
                            "description": "Role of the Profile",
                            "type": 8,
                            "required": True,
                        },
                    ],
                },
            ],
        },
    ],
}

commands = [authorize_commands]

headers = {"Authorization": f"Bot {discord_token}"}

if __name__ == "__main__":
    r = requests.post(url, headers=headers, json=server_commands)
    print(r.content.decode())