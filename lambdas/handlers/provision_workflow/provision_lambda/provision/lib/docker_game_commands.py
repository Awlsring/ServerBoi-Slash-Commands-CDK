def route_docker_command(**kwargs) -> str:
    game = kwargs["game"]

    docker_commands = {
        "valheim": form_valheim_command,
        "csgo": form_csgo_command,
        "ns2": form_ns2_command,
    }

    # TODO: Spaces in input names break docker command. Handle theses
    return docker_commands[game](**kwargs)


def form_user_data(docker_command: str) -> str:
    return f"""#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y

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

{docker_command}"""


def form_valheim_command(**kwargs) -> str:
    url = kwargs.get("url", None)
    server_name = kwargs.get("name", "ServerBoi-Valheim")
    world_name = kwargs.get("world-name", "ServerBoi-Valheim")

    url = kwargs.get("url", None)
    password = kwargs.get("password", "69420")
    interaction_token = kwargs.get("interaction_token")
    application_id = kwargs.get("application_id")
    execution_name = kwargs.get("execution_name")
    server_name = kwargs.get("name")

    command = f"sudo docker run -t -d \
    --net=host \
    --name serverboi-valheim \
    -e INTERACTION_TOKEN={interaction_token} \
    -e APPLICATION_ID={application_id} \
    -e EXECUTION_NAME={execution_name} \
    -e WORKFLOW_ENDPOINT={url} \
    -e SERVER_NAME='{server_name}' "

    overrides = {"MAP", "PASSWORD", "LIMIT"}

    for key, value in kwargs.items():
        if key.upper() in overrides:
            command = f"{command}-e {key.upper()}={value} "

    command = f"{command}serverboi/valheim:dev"

    return command


def form_ns2_command(**kwargs) -> str:
    url = kwargs.get("url", None)
    interaction_token = kwargs.get("interaction_token")
    application_id = kwargs.get("application_id")
    execution_name = kwargs.get("execution_name")
    server_name = kwargs.get("name")

    command = f"sudo docker run -t -d \
    --net=host \
    --name serverboi-ns2 \
    -e INTERACTION_TOKEN={interaction_token} \
    -e APPLICATION_ID={application_id} \
    -e EXECUTION_NAME={execution_name} \
    -e WORKFLOW_ENDPOINT={url} \
    -e SERVER_NAME='{server_name}' "

    for key, value in kwargs.items():
        command = f"{command}-e {key.upper()}={value} "

    command = f"{command}serverboi/ns2:dev"

    return command


def form_csgo_command(**kwargs) -> str:
    url = kwargs.get("url", None)
    interaction_token = kwargs.get("interaction_token")
    application_id = kwargs.get("application_id")
    execution_name = kwargs.get("execution_name")
    server_name = kwargs.get("name")
    gsl_token = kwargs.get("gsl-token")

    command = f"sudo docker run -t -d \
    --net=host \
    --name serverboi-csgo \
    -e INTERACTION_TOKEN={interaction_token} \
    -e APPLICATION_ID={application_id} \
    -e EXECUTION_NAME={execution_name} \
    -e WORKFLOW_ENDPOINT={url} \
    -e SERVER_NAME='{server_name}' \
    -e GSL_TOKEN={gsl_token} "

    for key, value in kwargs.items():
        key.replace("-", "_")
        command = f"{command}-e {key.upper()}={value} "

    command = f"{command}serverboi/csgo:dev"

    return command
