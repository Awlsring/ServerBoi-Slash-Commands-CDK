import requests
import discord
import json
from time import gmtime, strftime
from serverboi_utils.regions import Region
from serverboi_utils.states import translate_state

# https://azure.microsoft.com/en-us/global-infrastructure/geographies/#geographies
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
# https://cloud.google.com/compute/docs/regions-zones

def post_temp_response(interaction_id: str, interaction_token: str):
    temp_response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    temp_response = {"type": 5}
    post_temp_response = requests.post(temp_response_url, temp_response)
    print(f"Temp Response: {post_temp_response}")


def edit_response(application_id: str, interaction_token: str, data: dict):
    print(f"Data: {data}")
    update_url = f"https://discord.com/api/webhooks/{application_id}/{interaction_token}/messages/@original"
    response = requests.patch(update_url, json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"Payload delivered successfully, code {response.status_code}.")

def form_server_embed(
    server_name: str,
    server_id: str,
    ip: str,
    port: str,
    status: str,
    region: str,
    game: str,
    owner: str,
    service: str,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"{server_name}",
        color=discord.Color.blurple(),
        description=f"Connect: steam://connect/{ip}:{port}",
    )

    embed.set_thumbnail(url="https://i.kym-cdn.com/entries/icons/original/000/022/255/tumblr_inline_o58r6dmSfe1suaed2_500.gif")

    state, state_emoji = translate_state(service, status)

    if state == 'running':
        active = True
    else:
        active = False

    embed.add_field(name="Status", value=f"{state_emoji} {state}", inline=True)

    # Set address
    if ip != "" or ip != None:
        address = f"{ip}:{port}"
    else:
        address = "-"
    embed.add_field(name="Address", value=f"`{address}`", inline=True)

    # Line break
    embed.add_field(name="\u200B", value=f"\u200B", inline=True)

    # Get region
    sb_region = Region(region).regions[service.lower()]
    service_region = sb_region.name
    location = sb_region.location
    emoji = sb_region.emoji
    embed.add_field(name="Location", value=f"{emoji} {region} ({location})", inline=True)

    if not active:
        embed.add_field(name="\u200B", value=f"\u200B", inline=True)

    embed.add_field(name="Game", value=game, inline=True)

    if active:
        # TODO: Pull live player count
        embed.add_field(name="Players", value="x/x", inline=True)
    
    embed.set_footer(text=f"Owner: {owner} | 🖥️ Hosted on {service} in region {service_region} | 🕒 Pulled at {strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())} ")

    return embed


def form_response_data(**kwargs) -> dict:
    print(kwargs)
    embeds = kwargs.get("embeds")
    content = kwargs.get("content")

    data = {}

    if embeds:
        data["embeds"] = []
        for embed in embeds:
            embed_dict = embed.to_dict()
            data["embeds"].append(embed_dict)

    if content:
        data["content"] = content

    return data
