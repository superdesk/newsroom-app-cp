from newsroom.topics import TopicsResource, TopicsService
import superdesk


def init_app(app):
    TopicsResource.internal_resource = False
    superdesk.register_resource('topics', GlobalTopicsResource, GlobalTopicsService, _app=app)


class GlobalTopicsResource(TopicsResource):
    url = 'topics'
    resource_methods = ['GET', 'POST', 'DELETE']


class GlobalTopicsService(TopicsService):
    pass
