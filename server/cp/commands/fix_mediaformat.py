import time
from cp.signals import get_media_type_name, get_media_type_scheme
from newsroom.commands.cli import newsroom_cli
from superdesk.core import get_current_async_app


@newsroom_cli.command("fix_mediaformat")
async def fix_mediaformat(resource="items", limit=500, sleep_secs=2):
    """Fix MediaFormats in given resource"""
    await fix_media(resource, sleep_secs, limit)


async def fix_media(resource, sleep_secs=2, limit=500):
    service = get_current_async_app().resources.get_resource_service(resource)
    media_type_scheme = get_media_type_scheme()
    lookup = {
        "query": {
            "bool": {"must_not": {"term": {"subject.scheme": media_type_scheme}}}
        },
        "size": 100,
    }
    for i in range(int(limit)):
        items = await service.search(lookup)
        if not await items.count():
            break
        for item in await items.to_list_raw():
            updates = {"subject": item["subject"].copy() if item.get("subject") else []}
            updates["subject"].append(
                dict(
                    code="wiretext",
                    name=get_media_type_name("wiretext", item.get("language")),
                    scheme=media_type_scheme,
                )
            )
            await service.system_update(item["_id"], updates)
        print(".", end="", flush=True)
        time.sleep(int(sleep_secs))
    print("done.")
