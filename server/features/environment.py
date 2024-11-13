from superdesk.tests.environment import setup_before_all, setup_before_scenario

from newsroom.auth_server.oauth2 import generate_jwt_token, config_oauth
from cp.mgmt_api.app import get_app as _get_app
from cp.mgmt_api.default_settings import CORE_APPS


def get_app(*args, **kwargs):
    # explicitly set testing to True
    return _get_app(*args, testing=True, **kwargs)


class TestClient:
    client_id = "test"


def before_all(context):
    config = {
        "BEHAVE": True,
        "CORE_APPS": CORE_APPS,
        "INSTALLED_APPS": [],
        "ELASTICSEARCH_FORCE_REFRESH": True,
        "MGMT_API_ENABLED": True,
        "CACHE_TYPE": "null",
    }
    setup_before_all(context, config, app_factory=get_app)


def before_scenario(context, scenario):
    config = {
        "BEHAVE": True,
        "CORE_APPS": CORE_APPS,
        "INSTALLED_APPS": [],
        "ELASTICSEARCH_FORCE_REFRESH": True,
        "MGMT_API_ENABLED": True,
        "AUTH_SERVER_SHARED_SECRET": "test-secret",
        "CACHE_TYPE": "null",
    }

    setup_before_scenario(context, scenario, config, app_factory=get_app)

    with context.app.app_context():
        config_oauth(context.app)
        token = generate_jwt_token(
            TestClient(), "client_credentials", "test", ""
        ).decode()
        context.headers.append(("Authorization", f"Bearer {token}"))
