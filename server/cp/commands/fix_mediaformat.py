import time

from typing import get_args
from superdesk import get_resource_service
from cp.signals import get_media_type_name, get_media_type_scheme, MediaType
from newsroom.commands.manager import manager


@manager.command
def fix_mediaformat(
    resource="items", query="", code="wireaudio", limit=500, sleep_secs=2, dry_run=False
):
    if not query:
        print("Please provide a query to filter the items.")
        return
    if code not in get_args(MediaType):
        print("Invalid media type code.")
        return
    service = get_resource_service(resource)
    media_type_scheme = get_media_type_scheme()
    source = {
        "query": {
            "bool": {"must": {"query_string": {"query": query}}},
        },
        "size": 100,
        "from": 0,
    }
    for i in range(0, int(limit), source["size"]):
        source["from"] = i
        items = list(service.search(source))
        if not len(items):
            break
        for item in items:
            updates = {"subject": item["subject"].copy() if item.get("subject") else []}
            updates["subject"] = [
                s for s in updates["subject"] if s.get("scheme") != media_type_scheme
            ]
            updates["subject"].append(
                dict(
                    code=code,
                    name=get_media_type_name(code, item.get("language")),
                    scheme=media_type_scheme,
                )
            )

            if dry_run:
                print("Would update", item["_id"], "with", updates)
            else:
                print("Updating", item["_id"])
                service.system_update(item["_id"], updates, item)
        print(".", end="", flush=True)
        time.sleep(int(sleep_secs))
    print("done.")
