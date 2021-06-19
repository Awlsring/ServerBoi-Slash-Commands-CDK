from provision.lib.constants import SERVER_TABLE
from provision.lib.provision_classes.aws.aws_class import AWSProvision

# from provision.lib.provision_classes.linode.linode_class import LinodeProvision


def lambda_handler(event: dict, _) -> dict:
    game = event["game"]
    name = event.get("name", f"ServerBoi-{game}")
    user_id = event["user_id"]
    username = event["username"]
    service = event["service"]
    password = event.get("password", None)

    # pack event into a dict cause lambda flips if you try to **event -_-
    kwargs = {}
    for item, value in event.items():
        kwargs[item] = value

    service_workflows = {"aws": AWSProvision}

    workflow = service_workflows[service](**kwargs)
    server_id = workflow._generate_server_id()
    response = workflow.execute()

    server_item = {
        "ServerID": server_id,
        "OwnerID": user_id,
        "Owner": username,
        "Game": game,
        "Name": name,
        "Service": service,
    }

    if password:
        server_item["Password"] = password

    server_item.update(response)
    event.update(response)
    event["server_id"] = server_id

    try:
        SERVER_TABLE.put_item(Item=server_item)
    except Exception as error:
        raise Exception(error)

    return event
