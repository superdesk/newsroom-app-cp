from newsroom.topics import TopicsResource, TopicsService
import superdesk


def init_app(app):
    TopicsResource.internal_resource = False
    superdesk.register_resource('user_topics', UserTopicsResource, UserTopicsService, _app=app)


class UserTopicsResource(TopicsResource):
    resource_methods = ['GET', 'POST', 'DELETE']
    datasource = {
        "source": "topics",
    }


class UserTopicsService(TopicsService):
    pass
