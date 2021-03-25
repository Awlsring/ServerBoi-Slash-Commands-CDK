def lambda_handler(event, context):
    print(event)
    print(context)
    resp = {
        "type": 1,
        "event": event
    }
    return resp