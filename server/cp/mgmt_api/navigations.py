from newsroom.navigations import NavigationsResource, NavigationsService
import superdesk


def init_app(app):
    NavigationsResource.internal_resource = False
    superdesk.register_resource(
        "navigations", NavigationsResource, NavigationsService, _app=app
    )
