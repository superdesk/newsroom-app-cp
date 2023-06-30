import logging
import requests

from flask import current_app as app


logger = logging.getLogger(__name__)
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
    try:
        session.patch(
            url,
            json=payload,
            headers=headers,
            timeout=int(app.config.get("CEM_TIMEOUT", 10)),
            verify=bool(app.config.get("CEM_VERIFY_TLS", True)),
        )
    except requests.exceptions.RequestException as err:
        logger.error(err)
        return
    logger.info("Notification sent to CEM")
