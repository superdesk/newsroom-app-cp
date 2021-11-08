from newsroom.users import UsersResource, UsersService
import superdesk


def init_app(app):
    UsersResource.internal_resource = False
    UsersResource.public_methods = ["GET", "PATCH", "POST", "DELETE"]
    superdesk.register_resource('users', UsersResource, UsersService, _app=app)
