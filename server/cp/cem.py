import requests
from flask import current_app as app


session = requests.Session()


def send_notification(_type, user):
    url = app.config.get("CEM_URL", "")
    apikey = app.config.get("CEM_APIKEY", "")
    if not url or not apikey:
        return
    headers = {"x-api-key": apikey}
    payload = {
        "type": _type,
        "object_id": str(user["_id"]),
        "platform": app.config.get("CEM_PLATFORM"),
    }
    if user.get("company"):
        payload["company"] = str(user["company"])
    session.patch(
        url,
        timeout=5,
        json=payload,
        headers=headers,
    )
