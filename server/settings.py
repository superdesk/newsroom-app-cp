import pathlib

from newsroom.web.default_settings import CLIENT_CONFIG

SERVER_PATH = pathlib.Path(__file__).resolve().parent
CLIENT_PATH = SERVER_PATH.parent.joinpath("client")

SITE_NAME = 'CP Newshub'
COPYRIGHT_HOLDER = 'CP'

SERVICES = [
    {"name": "Domestic Sport", "code": "t"},
    {"name": "Overseas Sport", "code": "s"},
    {"name": "Finance", "code": "f"},
    {"name": "International News", "code": "i"},
    {"name": "Entertainment", "code": "e"},
]

SHOW_USER_REGISTER = False

NEWS_ONLY_FILTERS = []

LANGUAGES = ['en', 'fr_CA']
DEFAULT_LANGUAGE = 'en'

CLIENT_CONFIG.update({
    'display_news_only': False,  # Displays news only switch in wire

    'time_format': 'HH:mm',
    'date_format': 'MMM Do, YYYY',
    'locale_formats': {
        "en": {
            "TIME_FORMAT": "HH:mm",
            "DATE_FORMAT": "MMM Do, YYYY",
            "COVERAGE_DATE_FORMAT": "MMM Do, YYYY",
            "COVERAGE_DATE_TIME_FORMAT": "HH:mm MMM Do, YYYYY",
        },
        "fr_CA": {
            "TIME_FORMAT": "HH:mm",
            "DATE_FORMAT": "MMM Do, YYYY",
        },
    },
})
