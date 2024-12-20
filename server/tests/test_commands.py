from cp.commands.fix_mediaformat import fix_mediaformat


def test_fix_mediaformat(app):
    app.data.insert(
        "items",
        [
            {"_id": "en", "language": "en", "type": "text", "headline": "foo"},
            {"_id": "fr", "language": "fr", "type": "text", "headline": "bar"},
        ],
    )

    fix_mediaformat(query="headline:foo", code="wiretext", sleep_secs=0)

    en_item = app.data.find_one("items", req=None, _id="en")
    assert "subject" in en_item
    assert 1 == len(en_item["subject"])
    assert "wiretext" == en_item["subject"][0]["code"]
    assert "Wire text" == en_item["subject"][0]["name"]
    assert "mediaformat" == en_item["subject"][0]["scheme"]

    fr_item = app.data.find_one("items", req=None, _id="fr")
    assert "subject" not in fr_item, "Should not add subject to non-matching item"

    fix_mediaformat(query="headline:bar", code="wireaudio", sleep_secs=0)

    fr_item = app.data.find_one("items", req=None, _id="fr")
    assert "subject" in fr_item
    assert "wireaudio" == fr_item["subject"][0]["code"]
    assert "Audio fil de presse" == fr_item["subject"][0]["name"]
    assert "mediaformat" == fr_item["subject"][0]["scheme"]
