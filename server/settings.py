import pathlib
from flask_babel import lazy_gettext
from newsroom.web.default_settings import CLIENT_CONFIG, CORE_APPS as DEFAULT_CORE_APPS, \
    BLUEPRINTS as DEFAULT_BLUEPRINTS, CELERY_BEAT_SCHEDULE as DEFAULT_CELERY_BEAT_SCHEDULE


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
        "display_news_only": True,  # Displays news only switch in wire
        "time_format": "HH:mm",
        "date_format": "MMM Do, YYYY",
        "locale_formats": {
            "en": {
                "TIME_FORMAT": "HH:mm",
                "DATE_FORMAT": "MMM Do, YYYY",
                "COVERAGE_DATE_FORMAT": "MMM Do, YYYY",
                "COVERAGE_DATE_TIME_FORMAT": "HH:mm MMM Do, YYYY",
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
        "label": lazy_gettext("Ranking"),
    },
]

WIRE_AGGS = {
    "source": {"terms": {"field": "source", "size": 50}},
    "service": {"terms": {"field": "service.name", "size": 50}},
    "subject": {"terms": {"field": "subject.name", "size": 50}},
    "genre": {"terms": {"field": "genre.name", "size": 50}},
    "urgency": {"terms": {"field": "urgency"}},
}

AGENDA_GROUPS = WIRE_GROUPS

BLUEPRINTS = [
    blueprint
    for blueprint in DEFAULT_BLUEPRINTS
    if blueprint not in [
        "newsroom.design",
        "newsroom.monitoring",
        "newsroom.news_api.api_tokens"
    ]
]
BLUEPRINTS.extend([
    "cp.mgmt_api_docs"
])

CORE_APPS = [
    app
    for app in DEFAULT_CORE_APPS
    if app not in [
        "newsroom.monitoring",
        "newsroom.news_api",
        "newsroom.news_api.api_tokens",
        "newsroom.news_api.api_audit",
    ]
]

INSTALLED_APPS = [
    "cp.sidenav",
    "cp.signals",
]

WIRE_SUBJECT_SCHEME_WHITELIST = [
    "distribution",
    "subject_custom",
]

CELERY_BEAT_SCHEDULE = {
    key: val
    for key, val in DEFAULT_CELERY_BEAT_SCHEDULE.items()
    if key not in [
        "newsroom:monitoring_schedule_alerts",
        "newsroom:monitoring_immediate_alerts",
    ]
}
