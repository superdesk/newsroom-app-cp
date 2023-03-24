import cp
import bson
import responses
import cp.signals as signals

from responses import matchers


def test_on_publish_no_extended_headline():
    item = {"headline": "foo"}
    signals.on_publish_item(None, item)
    assert item["headline"] == "foo"


def test_on_publish_empty_extended_headline():
    item = {"headline": "foo", "extra": {cp.HEADLINE2: ""}}
    signals.on_publish_item(None, item)
    assert item["headline"] == "foo"


def test_on_publish_copy_extended_headline():
    item = {"headline": "foo", "extra": {cp.HEADLINE2: "bar"}}
    signals.on_publish_item(None, item)
    assert item["headline"] == "bar"


def test_on_publish_add_correction_to_body_html():
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
    user = {"_id": bson.ObjectId(), "email": "foo@example.com"}

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
                        "object_id": str(user["_id"]),
                        "type": "new user",
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
                        "type": "update user",
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
                        "type": "password change",
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
                        "type": "delete user",
                        "platform": "Test",
                    }
                ),
            ],
        )

        signals.on_user_deleted(None, user=user)


def test_language_agenda():
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
