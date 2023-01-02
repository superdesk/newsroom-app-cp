import cp

from newsroom.signals import publish_item


def on_publish_item(sender, item, **kwargs):
    copy_headline2_to_headline(item)
    copy_correction_to_body_html(item)


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


def init_app(app):
    publish_item.connect(on_publish_item)
