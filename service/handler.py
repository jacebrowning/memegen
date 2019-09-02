import json
import requests
import base64


def hello(event, context):
    resp = requests.get("https://memegen.link/iw/test_code/in_production.jpg")
    print(dir(resp))
    print(resp)
    response = {
        "statusCode": 200,
        "body": base64.b64encode(resp.content).decode("utf-8"),
        "headers": {"Content-Type": "image/jpeg"},
    }

    return response
