import time

from superdesk import get_resource_service
from cp.signals import get_media_type_name, get_media_type_scheme
from newsroom.commands.manager import manager


@manager.command
def fix_mediaformat(resource="items", limit=500, sleep_secs=2):
    service = get_resource_service(resource)
    media_type_scheme = get_media_type_scheme()
    source = {
        "query": {
            "bool": {"must_not": {"term": {"subject.scheme": media_type_scheme}}}
        },
        "size": 100,
    }
    for i in range(int(limit)):
        items = service.search(source)
        if not items.count():
            break
        for item in items:
            updates = {"subject": item["subject"].copy() if item.get("subject") else []}
            updates["subject"].append(
                dict(
                    code="wiretext",
                    name=get_media_type_name("wiretext", item.get("language")),
                    scheme=media_type_scheme,
                )
            )

            service.system_update(item["_id"], updates, item)
        print(".", end="", flush=True)
        time.sleep(int(sleep_secs))
    print("done.")
