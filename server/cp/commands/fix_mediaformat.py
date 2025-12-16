import time
import click
from cp.signals import get_media_type_name, get_media_type_scheme
from newsroom.commands.cli import newsroom_cli
from superdesk.core import get_current_async_app


@newsroom_cli.command("fix_mediaformat")
@click.option("--resource", default="items", help="Resource to fix media formats in.")
@click.option("--limit", default=500, type=int, help="Max number of iterations.")
@click.option(
    "--sleep-secs", default=2, type=int, help="Sleep time between batches (seconds)."
)
async def fix_mediaformat(resource, limit, sleep_secs):
    """Fix MediaFormats in given resource"""
    await fix_media(resource, sleep_secs, limit)


async def fix_media(resource, sleep_secs=2, limit=500):
    service = get_current_async_app().resources.get_resource_service(resource)
    media_type_scheme = get_media_type_scheme()
    lookup = {
        "query": {
            "bool": {"must": {"query_string": {"query": query}}},
        },
        "size": 100,
        "from": 0,
    }
    for i in range(int(limit)):
        items = await service.search(lookup)
        if not await items.count():
            break
        for item in await items.to_list_raw():
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
            await service.system_update(item["_id"], updates)
        print(".", end="", flush=True)
        time.sleep(int(sleep_secs))
    print("done.")
