from cp.commands.fix_mediaformat import fix_mediaformat


def test_fix_mediaformat(app):
    app.data.insert(
        "items",
        [
            {"_id": "en", "language": "en", "type": "text"},
            {"_id": "fr", "language": "fr", "type": "text"},
        ],
    )

    fix_mediaformat()

    en_item = app.data.find_one("items", req=None, _id="en")
    assert "subject" in en_item
    assert 1 == len(en_item["subject"])
    assert "wiretext" == en_item["subject"][0]["code"]
    assert "Wire text" == en_item["subject"][0]["name"]
    assert "mediaformat" == en_item["subject"][0]["scheme"]

    fr_item = app.data.find_one("items", req=None, _id="fr")
    assert "Texte fil de presse" == fr_item["subject"][0]["name"]
