import os
import pathlib
from flask_babel import lazy_gettext
from superdesk.default_settings import strtobool
from newsroom.web.default_settings import (
    env,
    CLIENT_CONFIG,
    CORE_APPS as DEFAULT_CORE_APPS,
    BLUEPRINTS as DEFAULT_BLUEPRINTS,
    CELERY_BEAT_SCHEDULE as DEFAULT_CELERY_BEAT_SCHEDULE,
    CLIENT_URL,
    CLIENT_LOCALE_FORMATS,
    AUTH_PROVIDERS,
)
from cp.common_settings import AUTH_PROVIDERS  # noqa


SERVER_PATH = pathlib.Path(__file__).resolve().parent
CLIENT_PATH = SERVER_PATH.parent.joinpath("client")
TRANSLATIONS_PATH = SERVER_PATH.joinpath("translations")

SITE_NAME = "CP NewsPro"
COPYRIGHT_HOLDER = "CP"
CONTACT_ADDRESS = None

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
DEFAULT_TIMEZONE = "America/Toronto"

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

# ``CLIENT_CONFIG`` references ``CLIENT_LOCALE_FORMATS`` by reference
# So we can safely update these dicts without needing to specify all formats
# And they will be all reflected in the ``CLIENT_CONFIG.locale_formats`` config
CLIENT_LOCALE_FORMATS["en"].update(
    {
        "TIME_FORMAT": "HH:mm",
        "DATE_FORMAT": "MMM Do, YYYY",
        "COVERAGE_DATE_FORMAT": "MMM Do, YYYY",
        "COVERAGE_DATE_TIME_FORMAT": "HH:mm MMM Do, YYYY",
        "DATE_FORMAT_HEADER": "long",  # babel
    }
)
CLIENT_LOCALE_FORMATS["fr_CA"].update(
    {
        "TIME_FORMAT": "HH:mm",
        "DATE_FORMAT": "Do MMMM YYYY",
        "COVERAGE_DATE_FORMAT": "LL",
        "DATETIME_FORMAT": "HH:mm [le] Do MMMM YYYY",
        "COVERAGE_DATE_TIME_FORMAT": "HH:mm [le] Do MMMM YYYY",
        "DATE_FORMAT_HEADER": "d MMMM yyyy à H:mm zzz",  # babel
        "AGENDA_DATE_FORMAT_SHORT": "dddd, D MMMM",
        "AGENDA_DATE_FORMAT_LONG": "dddd, D MMMM YYYY",
    }
)

CLIENT_CONFIG.update(
    {
        "coverage_types": COVERAGE_TYPES,
        "display_news_only": True,  # Displays news only switch in wire
        "display_all_versions_toggle": False,
        "display_agenda_featured_stories_only": False,
        "time_format": "HH:mm",
        "date_format": "MMM Do, YYYY",
        "default_timezone": DEFAULT_TIMEZONE,
        "filter_panel_defaults": {
            "tab": {
                "wire": "filters",
                "agenda": "filters",
            },
            "open": {
                "wire": True,
                "agenda": True,
            },
        },
        "advanced_search": {
            "fields": {
                "wire": ["headline", "slugline", "body_html"],
                "agenda": ["name", "description"],
            },
        },
    }
)

CLIENT_LOCALE_FORMATS = CLIENT_CONFIG["locale_formats"]

WIRE_GROUPS = [
    {
        "field": "language",
        "label": lazy_gettext("Language"),
    },
    {
        "field": "source",
        "label": lazy_gettext("Source"),
    },
    {
        "field": "service",
        "label": lazy_gettext("Wire Category"),
    },
    {
        "field": "subject_custom",
        "label": lazy_gettext("Subject"),
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "subject_custom",
        },
    },
    {
        "field": "genre",
        "label": lazy_gettext("Version"),
    },
]

WIRE_AGGS = {
    "language": {"terms": {"field": "language", "size": 50}},
    "source": {"terms": {"field": "source", "size": 50}},
    "service": {"terms": {"field": "service.name", "size": 50}},
    "subject": {"terms": {"field": "subject.name", "size": 100}},
    "genre": {"terms": {"field": "genre.name", "size": 50}},
}

AGENDA_GROUPS = [
    {
        "field": "language",
        "label": lazy_gettext("Language"),
    },
    {
        "field": "service",
        "label": lazy_gettext("Category"),
    },
    {
        "field": "event_types",
        "label": lazy_gettext("Event Type"),
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "event_types",
            "include_planning": True,
        },
    },
    {
        "field": "subject_custom",
        "label": lazy_gettext("Subject"),
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "subject_custom",
        },
    },
]


BLUEPRINTS = [
    "cp.auth",  # we need this one loaded before newsroom.auth to make it override logout
    "cp.mgmt_api_docs",
] + [
    blueprint
    for blueprint in DEFAULT_BLUEPRINTS
    if blueprint
    not in ["newsroom.design", "newsroom.monitoring", "newsroom.news_api.api_tokens"]
]


CORE_APPS = [
    app
    for app in DEFAULT_CORE_APPS
    if app
    not in [
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
    "newsroom.auth.saml",
]

WIRE_SUBJECT_SCHEME_WHITELIST = [
    "distribution",
    "subject_custom",
]

CELERY_BEAT_SCHEDULE = {
    key: val
    for key, val in DEFAULT_CELERY_BEAT_SCHEDULE.items()
    if key
    not in [
        "newsroom:monitoring_schedule_alerts",
        "newsroom:monitoring_immediate_alerts",
    ]
}

#: CPNHUB-98
MAXIMUM_FAILED_LOGIN_ATTEMPTS = 50

APM_SERVICE_NAME = "CP NewsPro"

CONTENT_API_EXPIRY_DAYS = 730

BABEL_DEFAULT_TIMEZONE = "America/Toronto"

# saml auth
SAML_LABEL = env("SAML_LABEL", "SSO")
SAML_COMPANY = env("SAML_COMPANY", "CP")
SAML_BASE_PATH = pathlib.Path(env("SAML_PATH", SERVER_PATH.joinpath("saml")))
SAML_PATH_MAP = {
    "localhost": "localhost",
    "uat": "uat",
}

for url, path in SAML_PATH_MAP.items():
    if url in CLIENT_URL:
        SAML_PATH = SAML_BASE_PATH.joinpath(path)
        break
else:
    SAML_PATH = SAML_BASE_PATH.joinpath("prod")

if SAML_PATH.joinpath("certs").exists():
    SAML_AUTH_ENABLED = True

CEM_URL = os.environ.get("CEM_URL", "")
CEM_APIKEY = os.environ.get("CEM_APIKEY", "")
CEM_PLATFORM = os.environ.get("CEM_PLATFORM", "MyNP")
CEM_VERIFY_TLS = strtobool(os.environ.get("CEM_VERIFY_TLS", "off"))

DEFAULT_ALLOW_COMPANIES_TO_MANAGE_PRODUCTS = True

AGENDA_SECTION = lazy_gettext("Calendar")
SAVED_SECTION = lazy_gettext("Bookmarks")

WIRE_SEARCH_FIELDS = [
    "slugline",
    "headline",
    "byline",
    "body_html",
    "body_text",
    "description_html",
    "description_text",
]

AGENDA_SHOW_MULTIDAY_ON_START_ONLY = True
