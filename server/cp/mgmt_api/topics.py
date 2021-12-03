from newsroom.topics import TopicsResource, TopicsService
import superdesk


def init_app(app):
    TopicsResource.internal_resource = False
    superdesk.register_resource('topics', UserTopicsResource, UserTopicsService, _app=app)


class UserTopicsResource(TopicsResource):
    item_url = r'regex("[a-f0-9]{24}")'
    resource_methods = ['GET', 'POST', 'DELETE']
    item_methods = ['PATCH']


class UserTopicsService(TopicsService):
    pass
