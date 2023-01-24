
import requests
from flask import current_app as app


session = requests.Session()


def send_notification(type, id):
    url = app.config.get("CEM_URL")
    if not url:
        return
    session.post(
        url,
        json={
            "type": type,
            "object_id": str(id),
            "platform": app.config.get("CEM_PLATFORM"),
        },
        timeout=5,
    )
