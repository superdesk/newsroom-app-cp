import superdesk
from . import oauth2
from superdesk.auth_server.scopes import allowed_scopes


def init_app(app):
    oauth2.config_oauth(app)
    superdesk.register_resource("auth_server_clients", AuthServerClientsResource, AuthServerClientsService, _app=app)


class AuthServerClientsResource(superdesk.Resource):

    schema = {
        "name": {
            "type": "string",
            "required": True,
            "unique": True,
        },
        "password": {"type": "string", "required": True},
        "scope": {"type": "list", "allowed": list(allowed_scopes), "required": True},
    }


class AuthServerClientsService(superdesk.Service):
    """Service to handle authorization server clients"""
