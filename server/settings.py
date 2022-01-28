import pathlib
from flask_babel import lazy_gettext
from newsroom.web.default_settings import CLIENT_CONFIG, CORE_APPS as _CORE_APPS


SERVER_PATH = pathlib.Path(__file__).resolve().parent
CLIENT_PATH = SERVER_PATH.parent.joinpath("client")

SITE_NAME = "CP NewsPro"
COPYRIGHT_HOLDER = "CP"

SERVICES = [
    {"name": "Domestic Sport", "code": "t"},
    {"name": "Overseas Sport", "code": "s"},
    {"name": "Finance", "code": "f"},
    {"name": "International News", "code": "i"},
    {"name": "Entertainment", "code": "e"},
]

SHOW_USER_REGISTER = True
NEWS_ONLY_FILTERS = []

LANGUAGES = ["en", "fr_CA"]
DEFAULT_LANGUAGE = "en"

CLIENT_CONFIG.update(
    {
        "display_news_only": False,  # Displays news only switch in wire
        "time_format": "HH:mm",
        "date_format": "MMM Do, YYYY",
        "locale_formats": {
            "en": {
                "TIME_FORMAT": "HH:mm",
                "DATE_FORMAT": "MMM Do, YYYY",
                "COVERAGE_DATE_FORMAT": "MMM Do, YYYY",
                "COVERAGE_DATE_TIME_FORMAT": "HH:mm MMM Do, YYYYY",
                "DATE_FORMAT_HEADER": "EEEE, MMMM d, yyyy",
            },
            "fr_CA": {
                "TIME_FORMAT": "HH:mm",
                "DATE_FORMAT": "MMM Do, YYYY",
                "DATE_FORMAT_HEADER": "EEEE, 'le' d MMMM yyyy",
            },
        },
    }
)

WIRE_GROUPS = [
    {
        "field": "source",
        "label": lazy_gettext("Source"),
    },
    {
        "field": "service",
        "label": lazy_gettext("Wire Category"),
    },
    {
        "field": "subject",
        "label": lazy_gettext("Index/Subject"),
    },
    {
        "field": "genre",
        "label": lazy_gettext("Version"),
    },
    {
        "field": "urgency",
        "label": lazy_gettext("News Value"),
    },
]

WIRE_AGGS = {
    "source": {"terms": {"field": "source", "size": 50}},
    "service": {"terms": {"field": "service.name", "size": 50}},
    "subject": {
        "terms": {
            "field": "subject.name",
            "size": 20,
            "include": [
                "Print",
                "Broadcast",
                "Print / Broadcast",
                "QuickHit",
                "NewsBase",
                "DataSpecials",
                "Sports",
                "Politics",
                "Business",
                "Health",
                "Environment",
                "Science",
                "Lifestyle",
                "Religion",
                "Education",
            ],
        }
    },
    "genre": {"terms": {"field": "genre.name", "size": 50}},
    "urgency": {"terms": {"field": "urgency"}},
}

CORE_APPS = [app for app in _CORE_APPS if app != 'newsroom.monitoring']
INSTALLED_APPS = [
    "cp.sidenav",
    "cp.signals",
]
