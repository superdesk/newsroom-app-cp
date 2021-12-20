
import cp

from newsroom.signals import publish_item


def on_publish_item(sender, item, **kwargs):
    try:
        item["headline"] = item["extra"][cp.HEADLINE2]
    except KeyError:
        pass


def init_app(app):
    publish_item.connect(on_publish_item)
