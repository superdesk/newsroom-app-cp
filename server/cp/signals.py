
import cp

from newsroom.signals import publish_item


def on_publish_item(sender, item, **kwargs):
    try:
        headline = item["extra"][cp.HEADLINE2]
    except KeyError:
        return
    else:
        if headline:
            item["headline"] = headline


def init_app(app):
    publish_item.connect(on_publish_item)
