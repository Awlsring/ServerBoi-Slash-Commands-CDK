import os
import awsgi
from serverboi_interactions_lambda.commands.server import route_server_command
from serverboi_interactions_lambda.commands.onboard import route_onboard_command
from serverboi_interactions_lambda.commands.create import route_create_command
import serverboi_utils.responses as response_utils
from discord_interactions import verify_key_decorator
from flask import (
    Flask,
    jsonify,
    request,
)

PUBLIC_KEY = os.environ.get("PUBLIC_KEY")
RESOURCES_BUCKET = os.environ.get("RESOURCES_BUCKET")
SERVER_TABLE = os.environ.get("SERVER_TABLE")
app = Flask(__name__)


@app.route("/discord", methods=["POST"])
@verify_key_decorator(PUBLIC_KEY)
def index() -> dict:

    print(request.json)
    if request.json["type"] == 1:
        return jsonify({"type": 1})
    else:

        interaction_id = request.json["id"]
        interaction_token = request.json["token"]
        application_id = request.json["application_id"]

        response_utils.post_temp_response(interaction_id, interaction_token)

        command = request.json["data"]["options"][0]["name"]

        command_response = route_command(command, request)
        print(command_response)

        response_utils.edit_response(
            application_id, interaction_token, command_response
        )

        return ("", 204)


def route_command(command: str, request: request) -> dict:

    commands = {
        "server": route_server_command,
        "onboard": route_onboard_command,
        "create": route_create_command,
    }

    return commands[command](request)


def lambda_handler(event, context):

    print(event)

    return awsgi.response(app, event, context, base64_content_types={"image/png"})
