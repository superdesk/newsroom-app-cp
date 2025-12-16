# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2025-10-15 11:44

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from superdesk.commands.data_updates import BaseDataUpdate
from newsroom.agenda.agenda_service import AgendaItemService


class DataUpdate(BaseDataUpdate):
    resource = "agenda"
    use_async_resources = True

    async def forwards(
        self, collection: AsyncIOMotorCollection, database: AsyncIOMotorDatabase
    ) -> None:
        service = AgendaItemService()

        # fix service translations
        async for item in collection.find(
            {"service.translations.0": {"$exists": True}}
        ):
            updates = {
                "service": [
                    {
                        "code": svc["code"],
                        "name": svc["name"],
                        "qcode": svc["qcode"],
                        "scheme": svc.get("scheme"),
                        "translations": (
                            {"name": svc["translations"].get("name", {})}
                            if "name" in svc.get("translations", {})
                            else {}
                        ),
                    }
                    for svc in item.get("service", [])
                ]
            }
            await service.system_update(item["_id"], updates)

        # fix state
        async for item in collection.find({"state": "draft"}):
            await service.system_update(item["_id"], {"state": "scheduled"})

    async def backwards(
        self, collection: AsyncIOMotorCollection, database: AsyncIOMotorDatabase
    ) -> None:
        pass
