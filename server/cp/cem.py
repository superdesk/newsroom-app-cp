
import requests
from flask import current_app as app


session = requests.Session()


def send_notification(_type, _id):
    url = app.config.get("CEM_URL")
    if not url:
        return
    session.post(
        url,
        json={
            "type": _type,
            "object_id": str(_id),
            "platform": app.config.get("CEM_PLATFORM"),
        },
        timeout=5,
    )
