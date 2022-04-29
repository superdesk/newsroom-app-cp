from bson import ObjectId
from flask import current_app as app

from newsroom.topics import TopicsResource, TopicsService
import superdesk
from superdesk.errors import SuperdeskApiError


def init_app(app):
    TopicsResource.internal_resource = False
    superdesk.register_resource('topics', GlobalTopicsResource, GlobalTopicsService, _app=app)


class GlobalTopicsResource(TopicsResource):
    url = 'topics'
    resource_methods = ['GET', 'POST', 'DELETE']


class GlobalTopicsService(TopicsService):
    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            user = doc.get('user')
            if user:
                doc['original_creator'] = user
                doc['version_creator'] = user
            elif not doc.get('is_global'):
                message = ("Please set is_global True, or provide user in the body.")
                raise SuperdeskApiError.badRequestError(message=message, payload=message)
            if doc.get('subscribers'):
                doc['subscribers'] = [ObjectId(sub) for sub in doc['subscribers']]

    def on_created(self, docs):
        super().on_created(docs)
        for doc in docs:
            app.cache.set(str(doc['_id']), doc)

    def on_update(self, updates, original):
        super().on_update(updates, original)
        app.cache.delete(str(original['_id']))
