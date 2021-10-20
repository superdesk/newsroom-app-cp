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

CLIENT_CONFIG.update({
    'display_news_only': True  # Displays news only switch in wire
})