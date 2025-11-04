from newsroom.agenda.agenda_service import AgendaItemService
from newsroom.commands.data_updates import Upgrade


async def test_data_update(app, runner):
    event = {
        "_id": "event1",
        "item_type": "event",
        "state": "draft",
        "name": "Agenda 1",
        "dates": {
            "start": "2025-10-15",
            "end": "2025-10-15",
        },
        "service": [
            {
                "code": "g",
                "name": "National",
                "qcode": "g",
                "scheme": "categories",
                "translations": {
                    "name": {
                        "en-CA": "National",
                        "fr-CA": "Nouvelles Générales",
                    }
                },
            },
            {
                "code": "n",
                "name": "Weather",
                "qcode": "n",
                "scheme": "categories",
                "translations": {
                    "0": "[",
                    "1": "o",
                    "2": "b",
                    "3": "j",
                    "4": "e",
                    "5": "c",
                    "6": "t",
                    "7": " ",
                    "8": "O",
                    "9": "b",
                    "10": "j",
                    "11": "e",
                    "12": "c",
                    "13": "t",
                    "14": "]",
                    "name": {"fr-CA": "Météo"},
                },
            },
        ],
    }

    service = AgendaItemService()
    await service.mongo_async.insert_one(event)
    await service.elastic.insert([event])

    cmd = Upgrade()
    await cmd.run("00001_20251015-114452_agenda")

    agenda = await AgendaItemService().find_by_id("event1")
    assert agenda
    assert agenda.service[1].translations == {"name": {"fr-CA": "Météo"}}
