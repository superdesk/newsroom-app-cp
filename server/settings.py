import pathlib
from flask_babel import lazy_gettext
from newsroom.web.default_settings import CLIENT_CONFIG, CORE_APPS as DEFAULT_CORE_APPS, \
    BLUEPRINTS as DEFAULT_BLUEPRINTS, CELERY_BEAT_SCHEDULE as DEFAULT_CELERY_BEAT_SCHEDULE


SERVER_PATH = pathlib.Path(__file__).resolve().parent
CLIENT_PATH = SERVER_PATH.parent.joinpath("client")
TRANSLATIONS_PATH = SERVER_PATH.joinpath("translations")

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

# Copied from Superdesk CV
COVERAGE_TYPES = {
    "text": {
        "name": "Text",
        "icon": "text",
        "translations": {"fr_ca": "Texte"},
    },
    "picture": {
        "name": "Picture",
        "icon": "photo",
        "translations": {"fr_ca": "Photo"},
    },
    "video": {
        "name": "Video",
        "icon": "video",
        "translations": {"fr_ca": "Vidéo"},
    },
    "audio": {
        "name": "Audio",
        "icon": "audio",
        "translations": {"fr_ca": "Audio"},
    },
    "infographics": {
        "name": "Infographics",
        "icon": "infographics",
        "translations": {"fr_ca": "Infographie"},
    },
    "live_video": {
        "name": "Live Video",
        "icon": "live-video",
        "translations": {"fr_ca": "Vidéo en direct"},
    },
    "live_blog": {
        "name": "Live Blog",
        "icon": "live-blog",
        "translations": {"fr_ca": "Blogue en direct"},
    },
}

CLIENT_CONFIG.update(
    {
        "coverage_types": COVERAGE_TYPES,
        "display_news_only": True,  # Displays news only switch in wire
        "display_all_versions_toggle": False,
        "time_format": "HH:mm",
        "date_format": "MMM Do, YYYY",
        "locale_formats": {
            "en": {
                "TIME_FORMAT": "HH:mm",
                "DATE_FORMAT": "MMM Do, YYYY",
                "COVERAGE_DATE_FORMAT": "MMM Do, YYYY",
                "COVERAGE_DATE_TIME_FORMAT": "HH:mm MMM Do, YYYY",
                "DATE_FORMAT_HEADER": "long",  # babel
            },
            "fr_CA": {
                "TIME_FORMAT": "HH:mm",
                "DATE_FORMAT": "Do MMMM YYYY",
                "COVERAGE_DATE_FORMAT": "LL",
                "DATETIME_FORMAT": "HH:mm [le] Do MMMM YYYY",
                "COVERAGE_DATE_TIME_FORMAT": "HH:mm [le] Do MMMM YYYY",
                "DATE_FORMAT_HEADER": "d. MMMM yyyy à H:mm",  # babel
                "AGENDA_DATE_FORMAT_SHORT": "dddd, D MMMM",
                "AGENDA_DATE_FORMAT_LONG": "dddd, D MMMM YYYY",
            },
        },
    }
)

CLIENT_LOCALE_FORMATS = CLIENT_CONFIG["locale_formats"]

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

AGENDA_GROUPS = [
    {
        "field": "service",
        "label": lazy_gettext("Wire Category"),
    },
    {
        "field": "subject",
        "label": lazy_gettext("Index/Subject"),
    }
]

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
    "cp.mgmt_api_docs",
    "cp.auth",
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
    "cp.auth",
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

#: CPNHUB-98
MAXIMUM_FAILED_LOGIN_ATTEMPTS = 50

APM_SERVICE_NAME = "CP NewsPro"

CONTENT_API_EXPIRY_DAYS = 730
