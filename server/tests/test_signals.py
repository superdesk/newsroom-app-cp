
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
