from superdesk.tests.environment import setup_before_all, setup_before_scenario

from cp.mgmt_api.app import get_app as _get_app
from cp.mgmt_api.default_settings import CORE_APPS


def get_app(*args, **kwargs):
    # explicitly set testing to True
    return _get_app(*args, testing=True, **kwargs)


def before_all(context):
    config = {
        'BEHAVE': True,
        'CORE_APPS': CORE_APPS,
        'INSTALLED_APPS': [],
        'ELASTICSEARCH_FORCE_REFRESH': True,
        'MGMT_API_ENABLED': True,
        'MGMT_API_AUTH_TYPE': 'cp.mgmt_api.auth.public',
    }
    setup_before_all(context, config, app_factory=get_app)


def before_scenario(context, scenario):
    config = {
        'BEHAVE': True,
        'CORE_APPS': CORE_APPS,
        'INSTALLED_APPS': [],
        'ELASTICSEARCH_FORCE_REFRESH': True,
        'MGMT_API_ENABLED': True,
        'MGMT_API_AUTH_TYPE': 'cp.mgmt_api.auth.public',
    }

    setup_before_scenario(context, scenario, config, app_factory=get_app)
