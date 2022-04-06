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
