import requests

from typing import Literal
from flask import current_app as app


session = requests.Session()


def send_notification(_type, user, id_key: Literal["_id", "email"] = "_id"):
    url = app.config.get("CEM_URL", "")
    apikey = app.config.get("CEM_APIKEY", "")
    if not url or not apikey:
        return
    headers = {"x-api-key": apikey}
    payload = {
        "type": _type,
        "object_id": str(user[id_key]),
        "platform": app.config.get("CEM_PLATFORM"),
    }
    if user.get("company") and id_key == "_id":
        payload["company"] = str(user["company"])
    session.patch(
        url,
        timeout=5,
        json=payload,
        headers=headers,
    )
