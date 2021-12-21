import superdesk
from . import oauth2
from superdesk.auth_server.clients import AuthServerClientsResource, AuthServerClientsService


def init_app(app):
    oauth2.config_oauth(app)
    superdesk.register_resource("auth_server_clients", AuthServerClientsResource, AuthServerClientsService, _app=app)
