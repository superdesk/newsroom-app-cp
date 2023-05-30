import superdesk

from bson.objectid import ObjectId
from newsroom.users import UsersResource, UsersService
from superdesk.errors import SuperdeskApiError
from flask import current_app as app


class CPUsersResource(UsersResource):
    url = "users"
    item_methods = ["GET", "PATCH", "PUT", "DELETE"]
    resource_methods = ["GET", "POST"]
    internal_resource = False


def init_app(app):
    superdesk.register_resource('users', CPUsersResource, CPUsersService, _app=app)


class CPUsersService(UsersService):
    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            if doc.get('user_type') != 'administrator' and not doc.get('company'):
                message = ("Company is required if user type is not administrator.")
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            locale = doc.get('locale')
            if locale and locale not in app.config['LANGUAGES']:
                message = ("Locale is not in configured list of locales.")
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            if doc.get('company'):
                doc['company'] = ObjectId(doc.get('company'))

    def check_permissions(self, doc, updates=None):
        """Avoid testing if user has permissions."""
        pass
