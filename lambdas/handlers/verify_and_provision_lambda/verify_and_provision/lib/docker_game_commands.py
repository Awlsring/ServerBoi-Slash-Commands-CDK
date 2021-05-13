def route_docker_command(**kwargs) -> str:
    game = kwargs["game"]

    docker_commands = {
        "valheim": form_valheim_command,
        "csgo": form_csgo_command,
    }

    return docker_commands[game](**kwargs)


def form_valheim_command(**kwargs) -> str:
    url = kwargs.get("url", None)
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
    -e WORKFLOW_ENDPOINT="{url}" \
    lloesche/valheim-server"""


def form_csgo_command(**kwargs) -> str:
    interaction_token = kwargs.get("interaction_token")
    application_id = kwargs.get("application_id")
    execution_name = kwargs.get("execution_name")
    url = kwargs.get("url", None)
    server_name = kwargs.get("name")
    gsl_token = kwargs.get("gsl-token")

    overrides = {
        "FPS-MAX",
        "TICK-RATE",
        "PORT",
        "TV-PORT",
        "CLIENT-PORT",
        "MAX-PLAYERS",
        "RCON-PASSWORD",
        "PASSWORD",
        "START-MAP",
        "MAP-GROUP",
        "GAME-TYPE",
        "GAME-MODE",
    }

    command = f"sudo docker run -d \
    --net=host \
    --name serverboi-csgo \
    -e INTERACTION_TOKEN={interaction_token} \
    -e APPLICATION_ID={application_id} \
    -e EXECUTION_NAME={execution_name} \
    -e WORKFLOW_ENDPOINT={url} \
    -e SERVER_NAME={server_name} \
    -e GSL_TOKEN={gsl_token} "

    for key, value in kwargs.items():
        if key.upper() in overrides:
            command = f"{command}-e {key.upper()}={value} "

    command = f"{command}serverboi/csgo:dev"

    return command
