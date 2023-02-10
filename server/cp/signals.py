import cp

from newsroom.signals import publish_item, user_created, user_updated, user_deleted

from cp.cem import send_notification


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


def on_user_created(sender, user, **kwargs):
    send_notification("new user", user)


def on_user_updated(sender, user, updates=None, **kwargs):
    if updates and updates.get("password"):
        send_notification("password change", user)
    else:
        send_notification("update user", user)


def on_user_deleted(sender, user, **kwargs):
    send_notification("delete user", user)


def init_app(app):
    publish_item.connect(on_publish_item)
    user_created.connect(on_user_created)
    user_updated.connect(on_user_updated)
    user_deleted.connect(on_user_deleted)
