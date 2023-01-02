import cp

from cp.signals import on_publish_item


def test_on_publish_no_extended_headline():
    item = {"headline": "foo"}
    on_publish_item(None, item)
    assert item["headline"] == "foo"


def test_on_publish_empty_extended_headline():
    item = {"headline": "foo", "extra": {cp.HEADLINE2: ""}}
    on_publish_item(None, item)
    assert item["headline"] == "foo"


def test_on_publish_copy_extended_headline():
    item = {"headline": "foo", "extra": {cp.HEADLINE2: "bar"}}
    on_publish_item(None, item)
    assert item["headline"] == "bar"


def test_on_publish_add_correction_to_body_html():
    item = {
        "body_html": "<p>some text</p><p>another one</p>",
        "extra": {"correction": "correction info"},
    }
    on_publish_item(None, item)
    assert (
        "<p>some text</p><p>another one</p>\n<p>correction info</p>"
        == item["body_html"]
    )
