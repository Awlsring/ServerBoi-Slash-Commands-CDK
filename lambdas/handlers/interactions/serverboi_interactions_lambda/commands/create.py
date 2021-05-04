from flask import request

def route_create_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {
        "valheim": create_valheim
    }

    return server_commands[server_command]()

def create_valheim(*args, **kwargs) -> str:
    service = args[0]
    region = args[1]
    name = args[2]
    world_name = args[3]
    password = args[4]
    user_id = args[5]
    game = args[6]
    world_file = kwargs.get("world_file")

    # verify account and user
    # look up game run book
    # provision server
    # verify server has started
    # Write to webhook server is done


    return response