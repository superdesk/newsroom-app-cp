import time
import click
from newsroom.commands.cli import newsroom_cli
from superdesk.core import get_current_async_app


@newsroom_cli.command("fix_language")
@click.option("--resource", default="items", help="The resource to update")
async def fix_language(resource, limit=50, sleep_secs=2):
    """Update Languages of items in given resource"""

    service = get_current_async_app().resources.get_resource_service(resource)

    lookup = {
        "query": {"terms": {"language": ["en-CA", "en-US", "fr-CA"]}},
        "size": 100,
    }

    for i in range(int(limit)):
        items = await service.search(lookup=lookup)
        if not await items.count():
            break
        for item in await items.to_list_raw():
            new_language = item.language.split("-")[0]
            item.language = new_language
            updates = {"language": item.language}
            await service.system_update(item.id, updates)
        print(".", end="", flush=True)
        time.sleep(int(sleep_secs))
    print(".")
