import cp
import bson
import pytest
import responses
import cp.signals as signals

from datetime import datetime, timedelta
from responses import matchers
from werkzeug.exceptions import HTTPException


def test_on_publish_no_extended_headline(app):
    item = {"headline": "foo"}
    signals.on_publish_item(None, item)
    assert item["headline"] == "foo"


def test_on_publish_empty_extended_headline(app):
    item = {"headline": "foo", "extra": {cp.HEADLINE2: ""}}
    signals.on_publish_item(None, item)
    assert item["headline"] == "foo"


def test_on_publish_copy_extended_headline(app):
    item = {"headline": "foo", "extra": {cp.HEADLINE2: "bar"}}
    signals.on_publish_item(None, item)
    assert item["headline"] == "bar"


def test_on_publish_add_correction_to_body_html(app):
    item = {
        "body_html": "<p>some text</p><p>another one</p>",
        "extra": {"correction": "correction info"},
    }
    signals.on_publish_item(None, item)
    assert (
        "<p>some text</p><p>another one</p>\n<p>correction info</p>"
        == item["body_html"]
    )


def test_cem_notification_on_user_changes(app):
    app.config.update(
        {
            "CEM_URL": "https://example.com",
            "CEM_APIKEY": "somekey",
            "CEM_PLATFORM": "Test",
        }
    )
    company_id = bson.ObjectId()
    app.data.insert(
        "companies",
        [
            {
                "_id": company_id,
                "name": "Example Company",
                "is_enabled": True,
                "auth_provider": "gip",
            }
        ],
    )
    user = {"_id": bson.ObjectId(), "email": "foo@example.com", "company": company_id}

    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        rsps.add(
            responses.PATCH,
            "https://example.com",
            match=[
                matchers.header_matcher(
                    {
                        "x-api-key": "somekey",
                    }
                ),
                matchers.json_params_matcher(
                    {
                        "object_id": str(user["email"]),
                        "type": "new",
                        "platform": "Test",
                    }
                ),
            ],
        )

        signals.on_user_created(None, user=user, foo=1)

    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        rsps.add(
            responses.PATCH,
            "https://example.com",
            match=[
                matchers.json_params_matcher(
                    {
                        "object_id": str(user["_id"]),
                        "company": str(company_id),
                        "type": "update",
                        "platform": "Test",
                    }
                ),
            ],
        )

        signals.on_user_updated(None, user=user, foo=1)

    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        rsps.add(
            responses.PATCH,
            "https://example.com",
            match=[
                matchers.json_params_matcher(
                    {
                        "object_id": str(user["_id"]),
                        "company": str(company_id),
                        "type": "password",
                        "platform": "Test",
                    }
                ),
            ],
        )

        signals.on_user_updated(None, user=user, updates={"password": "bar"})

    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        rsps.add(
            responses.PATCH,
            "https://example.com",
            match=[
                matchers.json_params_matcher(
                    {
                        "object_id": str(user["_id"]),
                        "company": str(company_id),
                        "type": "delete",
                        "platform": "Test",
                    }
                ),
            ],
        )

        signals.on_user_deleted(None, user=user)


def test_cem_notification_for_non_google_auth(app, mocker):
    sub = mocker.patch("cp.signals.send_notification")
    app.config.update(
        {
            "CEM_URL": "https://example.com",
            "CEM_APIKEY": "somekey",
            "CEM_PLATFORM": "Test",
        }
    )
    company_id = bson.ObjectId()
    app.data.insert(
        "companies",
        [
            {
                "_id": company_id,
                "name": "Example Company",
                "is_enabled": True,
                "auth_provider": "azure",
            }
        ],
    )
    user = {"_id": bson.ObjectId(), "email": "foo@example.com", "company": company_id}

    signals.on_user_created(None, user=user, foo=1)
    assert len(sub.mock_calls) == 0

    signals.on_user_updated(None, user=user, foo=1)
    assert len(sub.mock_calls) == 0

    signals.on_user_updated(None, user=user, updates={"password": "bar"})
    assert len(sub.mock_calls) == 0

    signals.on_user_deleted(None, user=user)
    assert len(sub.mock_calls) == 0


def test_language_agenda(app):
    item = {"language": "en-CA"}
    signals.init_app(None)
    signals.push.send(None, item=item)
    assert "en" == item["language"]
    item["language"] = "en_CA"
    signals.push.send(None, item=item)
    assert "en" == item["language"]
    item["language"] = "fr-ca"
    signals.push.send(None, item=item)
    assert "fr" == item["language"]


def test_push_abort_missing_version(app):
    item = {"evolvedfrom": "foo", "subject": [{"scheme": "mediaformat"}]}
    with pytest.raises(HTTPException):
        signals.on_push(None, item=item)

    app.data.insert("items", [{"_id": "foo"}])
    signals.on_push(None, item=item)


def test_handle_transcripts(app):
    text_item = {"source": "CP", "subject": []}
    signals.on_publish_item(None, text_item)
    assert 1 == len(text_item["subject"])
    assert "mediaformat" == text_item["subject"][0]["scheme"]
    assert "wiretext" == text_item["subject"][0]["code"]
    assert "Wire text" == text_item["subject"][0]["name"]

    text_item = {"source": "CP", "subject": [], "language": "fr_CA"}
    signals.on_publish_item(None, text_item)
    assert "Texte fil de presse" == text_item["subject"][0]["name"]

    transcript_item = {
        "source": "TVEyes",
        "subject": [
            {"code": "tvstation", "name": "TV Station", "scheme": "mediaformat"},
            {"code": "CITY24", "name": "CP24 (CITY24)", "scheme": "station"},
        ],
    }

    signals.on_publish_item(None, transcript_item)
    assert "CP24 (CITY24)" == transcript_item["source"]
    assert "TV Station" == transcript_item["subject"][0]["name"]
    assert "expiry" in transcript_item
    assert (
        datetime.now()
        < transcript_item["expiry"]
        < datetime.now() + timedelta(days=100)
    )

    transcript_item["language"] = "fr-CA"
    signals.on_publish_item(None, transcript_item)
    assert 1 == len(transcript_item["subject"])
    assert "Station de télé" == transcript_item["subject"][0]["name"]


def test_wire_labels(app):
    def get_label(item):
        return next(
            (
                s
                for s in item.get("subject", [])
                if s.get("scheme") == cp.WIRE_LABELS_SCHEME
            ),
            None,
        )

    def assert_label(item, code, name):
        label = get_label(item)
        assert label is not None
        assert label["code"] == code
        assert label["name"] == name

    item = {}
    signals.on_publish_item(None, item)
    label = get_label(item)
    assert label is None

    item = {"slugline": "Something-The-Latest"}
    signals.on_publish_item(None, item)
    assert_label(item, "latest", "THE LATEST")

    item = {"genre": [{"code": "NewsAlert", "name": "NewsAlert"}]}
    signals.on_publish_item(None, item)
    assert_label(item, "alert", "ALERT")

    item = {"service": [{"code": "m", "name": "Advisory"}]}
    signals.on_publish_item(None, item)
    assert_label(item, "advisory", "ADVISORY")

    item = {"service": [{"code": "p", "name": "Press Release"}]}
    signals.on_publish_item(None, item)
    assert_label(item, "press-release", "PRESS RELEASE")
