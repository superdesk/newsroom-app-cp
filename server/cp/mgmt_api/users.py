import newsroom
import superdesk

from bson.objectid import ObjectId
from pymongo.collation import Collation
from flask import current_app as app
from newsroom.users.users import UsersResource, UsersService
from superdesk.errors import SuperdeskApiError
from typing_extensions import override

from cp.mgmt_api.utils import validate_product_refs


class CPUsersResource(newsroom.Resource):
    url = "users"
    schema = UsersResource.schema.copy()
    datasource = UsersResource.datasource.copy()
    item_methods = ["GET", "PATCH", "PUT", "DELETE"]
    resource_methods = ["GET", "POST"]
    collation = False


def init_app(app):
    superdesk.register_resource('users', CPUsersResource, CPUsersService, _app=app)


class CPUsersService(UsersService):
    @override
    def check_permissions(self, doc, updates=None):
        """Avoid testing if user has permissions."""
        pass

    @override
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
            if doc.get("products"):
                validate_product_refs(doc["products"])

    @override
    def on_update(self, updates, original):
        if updates.get("products"):
            validate_product_refs(updates["products"])

    @override
    def get(self, req, lookup):
        """"""
        cursor = super().get(req, lookup)
        cursor.collation(Collation(locale='en', strength=1))
        return cursor
