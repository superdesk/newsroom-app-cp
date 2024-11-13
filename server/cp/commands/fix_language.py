import time

from superdesk import get_resource_service
from newsroom.commands.manager import manager


@manager.command
def fix_language(resource="items", limit=50, sleep_secs=2):
    service = get_resource_service(resource)

    source = {
        "query": {"terms": {"language": ["en-CA", "en-US", "fr-CA"]}},
        "size": 100,
    }

    for i in range(int(limit)):
        items = service.search(source)
        if not items.count():
            break
        for item in items:
            updates = {"language": item["language"].split("-")[0]}
            service.system_update(item["_id"], updates, item)
        print(".", end="", flush=True)
        time.sleep(int(sleep_secs))
    print(".")
