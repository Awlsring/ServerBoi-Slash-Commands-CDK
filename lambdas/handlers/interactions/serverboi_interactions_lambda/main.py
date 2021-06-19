import os
import awsgi
from serverboi_interactions_lambda.commands.server import (
    route_server_command,
    server_start,
    server_stop,
)
from serverboi_interactions_lambda.commands.onboard import route_onboard_command
from serverboi_interactions_lambda.commands.create import route_create_command
import serverboi_utils.responses as response_utils
from discord_interactions import verify_key_decorator
from serverboi_interactions_lambda.lib.constants import PUBLIC_KEY
from flask import (
    Flask,
    jsonify,
    request,
)

app = Flask(__name__)


@app.route("/discord", methods=["POST"])
@verify_key_decorator(PUBLIC_KEY)
def index() -> dict:

    print(request.json)
    interaction_type = request.json["type"]
    interaction_id = request.json["id"]
    interaction_token = request.json["token"]
    application_id = request.json["application_id"]

    if interaction_type == 1:
        return jsonify({"type": 1})
    else:
        # Send temp response
        response_utils.post_temp_response(interaction_id, interaction_token)

        if interaction_type == 2:
            command = request.json["data"]["options"][0]["name"]

            command_response = route_command(command, request)

        if interaction_type == 3:
            button = request.json["data"]["custom_id"]
            command_dict = translate_button_cutom_id(button)

            server_commands = {"start": server_start, "stop": server_stop}

            command_response = server_commands[command_dict["command"]](**command_dict)

        print(command_response)

        response_utils.edit_response(
            application_id, interaction_token, command_response
        )

        return ("", 200)


def route_command(command: str, request: request) -> dict:

    commands = {
        "server": route_server_command,
        "onboard": route_onboard_command,
        "create": route_create_command,
    }

    return commands[command](request)


def translate_button_cutom_id(custom_id: str) -> dict:
    split_field = custom_id.split(".")
    return {"id": split_field[0], "command": split_field[1]}


def lambda_handler(event, context):

    print(event)

    return awsgi.response(app, event, context, base64_content_types={"image/png"})
