def route_docker_command(game: str, **kwargs) -> str:

    docker_commands = {
        "valheim": form_valheim_command,
        "csgo": form_csgo_command,
    }

    return docker_commands[game](**kwargs)


def form_valheim_command(**kwargs) -> str:
    server_name = kwargs.get("name", "ServerBoi-Valheim")
    world_name = kwargs.get("world-name", "ServerBoi-Valheim")
    password = kwargs.get("password", "69420")

    return f"""mkdir -p /valheim-server/config/worlds /valheim-server/data
    
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
    lloesche/valheim-server"""


def form_csgo_command(**kwargs) -> str:
    interaction_id = kwargs.get("interaction_id")
    application_id = kwargs.get("application_id")
    execution_name = kwargs.get("execution_id")
    server_name = kwargs.get("name")

    return f"""sudo docker run -d \
    --name csgo-server \
    -e INTERACTION_ID={interaction_id} \
    -e APPLICATION_ID={application_id} \
    -e EXECUTION_NAME={execution_name} \
    -e SERVER_NAME={server_name}
    serverboi/csgo:latest"""
