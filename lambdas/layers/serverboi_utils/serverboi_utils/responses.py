import requests


def post_temp_response(interaction_id: str, interaction_token: str):
    temp_response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    temp_response = {"type": 5, "data": {"flags": 64}}
    post_temp_response = requests.post(temp_response_url, json=temp_response)
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
        print(f"Edit Response: {response}.")


def post_new_reponse(application_id: str, interaction_token: str, data: dict):
    print(f"Data: {data}")
    update_url = (
        f"https://discord.com/api/webhooks/{application_id}/{interaction_token}"
    )
    response = requests.post(update_url, json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"Edit Response: {response}.")


def form_response_data(**kwargs) -> dict:
    print(kwargs)
    embeds = kwargs.get("embeds")
    content = kwargs.get("content")

    data = {"flags": 64}

    if embeds:
        data["embeds"] = []
        for embed in embeds:
            embed_dict = embed.to_dict()
            data["embeds"].append(embed_dict)

    if content:
        data["content"] = content

    return data
