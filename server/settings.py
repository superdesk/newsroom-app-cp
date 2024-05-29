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
    CONTENTAPI_ELASTICSEARCH_SETTINGS,
)
from cp.common_settings import AUTH_PROVIDERS  # noqa


SERVER_PATH = pathlib.Path(__file__).resolve().parent
CLIENT_PATH = SERVER_PATH.parent.joinpath("client")
TRANSLATIONS_PATH = SERVER_PATH.joinpath("translations")

SITE_NAME = "CP NewsPro"
COPYRIGHT_HOLDER = "CP"
CONTACT_ADDRESS = None
DOWNLOAD_RENDITION = "original"

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
        # server formats
        "DATE_FORMAT_HEADER": "long",
    }
)
CLIENT_LOCALE_FORMATS["fr_CA"].update(
    {
        "TIME_FORMAT": "HH:mm",
        "DATE_FORMAT": "Do MMMM YYYY",
        "DATETIME_FORMAT": "HH:mm [le] Do MMMM YYYY",
        "COVERAGE_DATE_FORMAT": "LL",
        "COVERAGE_DATE_TIME_FORMAT": "HH:mm [le] Do MMMM YYYY",
        "AGENDA_DATE_FORMAT_SHORT": "dddd, D MMMM",
        "AGENDA_DATE_FORMAT_LONG": "dddd, D MMMM YYYY",
        # server formats
        "DATE_FORMAT_HEADER": "d MMMM yyyy à H:mm zzz",
        "NOTIFICATION_EMAIL_TIME_FORMAT": "HH:mm",
        "NOTIFICATION_EMAIL_DATE_FORMAT": "d MMMM yyyy",
        "NOTIFICATION_EMAIL_DATETIME_FORMAT": "d MMMM yyyy à H:mm",
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
        "view_content_tooltip_email": "help-aide@thecanadianpress.com",
        "searchbar_threshold_value": 30,
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
        "coverage_status_filter": {
            "not planned": {
                "enabled": True,
                "index": 1,
                "option_label": lazy_gettext("No coverage"),
                "button_label": lazy_gettext("No coverage"),
            },
            "not intended": {
                "enabled": True,
                "index": 2,
                "option_label": lazy_gettext("Cancelled / not planned"),
                "button_label": lazy_gettext("Cancelled / not planned"),
            },
            "may be": {
                "enabled": True,
                "index": 3,
                "option_label": lazy_gettext("Not decided / on merit"),
                "button_label": lazy_gettext("Not decided / on merit"),
            },
            "planned": {
                "enabled": True,
                "index": 4,
                "option_label": lazy_gettext("Planned"),
                "button_label": lazy_gettext("Planned"),
            },
            "completed": {
                "enabled": True,
                "index": 5,
                "option_label": lazy_gettext("Completed"),
                "button_label": lazy_gettext("Completed"),
            },
        },
        "agenda_top_story_scheme": "topstory",
    },
)

CLIENT_LOCALE_FORMATS = CLIENT_CONFIG["locale_formats"]

WIRE_GROUPS = [
    {
        "field": "language",
        "label": lazy_gettext("Language"),
    },
    {
        "field": "mediaformat",
        "label": lazy_gettext("Media type"),
        "nested": {
            "parent": "subject",
            "field": "scheme",
            "value": "mediaformat",
        },
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
    "newsroom.auth.saml",
]

WIRE_SUBJECT_SCHEME_WHITELIST = [
    "distribution",
    "subject_custom",
    "mediaformat",
    "station",
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

is_test_instance = any([url in CLIENT_URL for url in ["cp-dev.", "cpcn-uat.", "test."]])
AUTH_FIREBASE_AUDIENCE = "cp-identity-dev" if is_test_instance else "cp-identity"

CEM_URL = os.environ.get("CEM_URL", "")
CEM_APIKEY = os.environ.get("CEM_APIKEY", "")
CEM_PLATFORM = os.environ.get("CEM_PLATFORM", "MyNP")
CEM_VERIFY_TLS = strtobool(os.environ.get("CEM_VERIFY_TLS", "off"))
CEM_TIMEOUT = int(os.environ.get("CEM_TIMEOUT") or 10)

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

WIRE_NOTIFICATIONS_ON_CORRECTIONS = True

CONTENTAPI_ELASTICSEARCH_SETTINGS["settings"]["analysis"]["analyzer"][
    "html_field_analyzer"
]["filter"] = [
    "lowercase",
    "elision",
    "asciifolding",
]

# bump core versions to reindex inclusing elision
WIRE_SCHEMA_VERSION = 4
AGENDA_SCHEMA_VERSION = 6

SOURCE_EXPIRY_DAYS = {}

AGENDA_CSV_SUBJECT_SCHEMES = ["subject_custom"]

EMAIL_DEFAULT_SENDER_NAME = "CP NewsPro"
EMAIL_SENDER_NAME_LANGUAGE_MAP = {
    "en": "CP NewsPro",
    "fr_ca": "PC NouvellesPro",
}

PRODUCTFRUITS_WORKSPACE_CODE = os.environ.get("PRODUCTFRUITS_WORKSPACE_CODE")

PERSONAL_DASHBOARD_CARD_TYPE = "6-text-only"

ALL_DAY_DATE_FORMAT = "%d/%m/%Y"
