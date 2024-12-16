import cp
import flask

from typing import Literal, Optional
from flask import current_app as app
from quart_babel import gettext

from datetime import datetime, timedelta
from superdesk import get_resource_service
from newsroom.types import User, Company
from newsroom.signals import (
    publish_item,
    user_created,
    user_updated,
    user_deleted,
    push,
)

from cp.cem import send_notification


def fix_language(lang) -> str:
    return lang.split("-")[0].split("_")[0].lower()


def on_publish_item(sender, item, **kwargs):
    copy_headline2_to_headline(item)
    copy_correction_to_body_html(item)
    handle_transcripts(item)
    set_wire_labels(item)


def copy_headline2_to_headline(item):
    try:
        headline = item["extra"][cp.HEADLINE2]
    except KeyError:
        return
    else:
        if headline:
            item["headline"] = headline


def copy_correction_to_body_html(item):
    if item.get("extra") and item["extra"].get(cp.CORRECTION):
        item.setdefault("body_html", "")
        item["body_html"] = "{}\n<p>{}</p>".format(
            item["body_html"], item["extra"][cp.CORRECTION]
        )


def on_user_created(sender, user, **kwargs):
    if user_auth_is_gip(user):
        send_notification("new", user, id_key="email")


def on_user_updated(sender, user, updates=None, **kwargs):
    if user_auth_is_gip(user):
        if updates and updates.get("password"):
            send_notification("password", user)
        else:
            send_notification("update", user)


def on_user_deleted(sender, user, **kwargs):
    if user_auth_is_gip(user):
        send_notification("delete", user)


def on_push(sender, item, **kwargs):
    if item.get("language"):
        item["language"] = fix_language(item["language"])

    if get_media_type(item) and item.get("evolvedfrom"):
        parent_item = get_resource_service("items").find_one(
            req=None, _id=item["evolvedfrom"]
        )
        if parent_item is None:
            flask.abort(503)  # must be 50x error to trigger retry later


def user_auth_is_gip(user: User) -> bool:
    if not user.get("company"):
        return False

    company: Optional[Company] = get_resource_service("companies").find_one(
        req=None, _id=user["company"]
    )
    if not company:
        return False

    return company.get("auth_provider") == "gip"


def get_media_type(item):
    media_type_scheme = get_media_type_scheme()
    return next(
        (s for s in item.get("subject", []) if s.get("scheme") == media_type_scheme),
        None,
    )


def handle_transcripts(item):
    item.setdefault("subject", [])
    media_type_scheme = get_media_type_scheme()
    media_type = get_media_type(item)
    media_source_scheme = app.config.get("MEDIA_SOURCE_SCHEME", "station")
    media_source = next(
        (s for s in item["subject"] if s.get("scheme") == media_source_scheme), None
    )

    if not media_type:  #
        item["subject"].append(
            dict(
                name=get_media_type_name("wiretext", item.get("language")),
                code="wiretext",
                scheme=media_type_scheme,
            )
        )
        return

    if "fr" in item.get("language", "en"):
        media_type["name"] = get_media_type_name(media_type["code"], item["language"])

    if media_source:
        item["source"] = media_source.get("name") or media_source.get("code")
        item["subject"] = [
            s for s in item["subject"] if s.get("scheme") != media_source_scheme
        ]

    if media_type and media_type["code"] in ("tvstation", "radionstation"):
        # it might be already populated based on previous segment
        item.setdefault("expiry", datetime.utcnow() + timedelta(days=90))


MediaType = Literal["radionstation", "tvstation", "wireaudio", "wiretext"]
MEDIA_TYPE_NAMES = {
    "wiretext": ("Wire text", "Texte fil de presse"),
    "wireaudio": ("Wire audio", "Audio fil de presse"),
    "tvstation": ("TV station", "Station de télé"),
    "radiostation": ("Radio station", "Station de radio"),
}


def get_media_type_scheme():
    return app.config.get("MEDIA_TYPE_CV", "mediaformat")


def get_media_type_name(scheme: MediaType, language: Optional[str] = "en") -> str:
    return MEDIA_TYPE_NAMES[scheme][1 if language and "fr" in language else 0]


def item_has_code(item, field: Literal["genre", "service"], code: str) -> bool:
    values = item.get(field) or []
    return any(value.get("code") == code for value in values)


def append_subject(item, name: str, code: str) -> None:
    item.setdefault("subject", []).append(
        dict(
            name=name,
            code=code,
            scheme=cp.WIRE_LABELS_SCHEME,
        )
    )


def set_wire_labels(item):
    if item.get("slugline") and "-The-Latest" in item["slugline"]:
        append_subject(item, gettext("THE LATEST"), "latest")

    if item_has_code(item, "genre", "NewsAlert"):
        append_subject(item, gettext("ALERT"), "alert")

    if item_has_code(item, "service", "m"):
        append_subject(item, gettext("ADVISORY"), "advisory")

    if item_has_code(item, "service", "p"):
        append_subject(item, gettext("PRESS RELEASE"), "press-release")


def init_app(app):
    publish_item.connect(on_publish_item)
    user_created.connect(on_user_created)
    user_updated.connect(on_user_updated)
    user_deleted.connect(on_user_deleted)
    push.connect(on_push)
