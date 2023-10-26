import logging
import requests

from typing import Literal
from flask import current_app as app


logger = logging.getLogger(__name__)
session = requests.Session()


def send_notification(_type, user, id_key: Literal["_id", "email"] = "_id"):
    url = app.config.get("CEM_URL", "")
    apikey = app.config.get("CEM_APIKEY", "")
    if not url or not apikey:
        logger.warning("CEM is not configured")
        return
    logger.info("Sending notification to CEM for %s", _type)
    headers = {"x-api-key": apikey, "Content-Type": "application/json"}
    payload = {
        "type": _type,
        "object_id": str(user[id_key]),
        "platform": app.config.get("CEM_PLATFORM"),
    }
    if user.get("company") and id_key == "_id":
        payload["company"] = str(user["company"])
    try:
        resp = session.patch(
            url,
            json=payload,
            headers=headers,
            timeout=int(app.config.get("CEM_TIMEOUT", 10)),
            verify=bool(app.config.get("CEM_VERIFY_TLS", True)),
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        logger.error(err)
    else:
        logger.info("Notification sent to CEM for %s", _type)
