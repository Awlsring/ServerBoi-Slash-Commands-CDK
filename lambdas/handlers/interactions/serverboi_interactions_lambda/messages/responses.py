import requests
import discord
import json


def post_temp_response(interaction_id: str, interaction_token: str):
    temp_response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    temp_response = {"type": 5}
    post_temp_response = requests.post(temp_response_url, temp_response)
    print(f"Temp Response: {post_temp_response}")


def edit_response(application_id: str, interaction_token: str, data: dict):
    update_response = {"type": 4, "data": data}
    update_url = f"https://discord.com/api/v8/webhooks/{application_id}/{interaction_token}/messages/@original"
    update_response = requests.patch(update_url, update_response)
    print(f"Update Response: {update_response}")


def get_owner_from_id(user_id: str):
    return discord.Client().get_user(user_id)


def form_server_embed(
    server_name: str,
    server_id: str,
    ip: str,
    port: str,
    status: str,
    location: str,
    game: str,
    owner: str,
    service: str,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"{server_name}",
        color=discord.Color.blurple(),
        description=f"Connect: steam://connect/{ip}:{port}",
    )

    embed.set_thumbnail(url="image_url")

    # TODO: Pull status and and correct light emoji
    embed.add_field(name="Status", value=f"🟢 {status}", inline=True)
    embed.add_field(name="Address", value=f"`{ip}:{port}`", inline=True)

    # TODO: Pull location and convert to generic and flag
    embed.add_field(name="Location", value=f"🇺🇸 {location}", inline=True)

    embed.add_field(name="Game", value=game, inline=True)
    embed.set_footer(text=f"Owner: {owner}. Hosted on {service}")

    return embed


def form_response_data(**kwargs) -> dict:
    data = json.dumps(kwargs)

    return data
