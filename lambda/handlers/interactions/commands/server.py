from flask import request

def route_server_command(request):

    server_command = request.json["data"]["options"][0]['options'][0]['name']

    server_commands = {
        'status': server_status,
        'start': server_start,
        'stop': server_stop,
    }

    server_id = request.json["data"]["options"][0]['options'][0]['options'][0]['value']
    return server_commands[server_command](server_id)

def server_start(id):
    response = f'Placeholder response for server start. Server {id} was entered'
    return response

def server_stop(id):
    response = f'Placeholder response for server stop. Server {id} was entered'
    return response

def server_status(id):
    response = f'Placeholder response for server status. Server {id} was entered'
    return response