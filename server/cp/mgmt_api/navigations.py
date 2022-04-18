from bson import ObjectId

from newsroom.navigations import NavigationsResource, NavigationsService
import superdesk


def init_app(app):
    NavigationsResource.internal_resource = False
    superdesk.register_resource('navigations', NavigationsResource, CPNavigationsService, _app=app)


class CPNavigationsService(NavigationsService):
    def on_delete(self, doc):
        super().on_delete(doc)
        navigation = ObjectId(doc.get('_id'))
        products = superdesk.get_resource_service('products').find(where={'navigations': navigation})
        for product in products:
            product['navigations'].remove(navigation)
            superdesk.get_resource_service('products').patch(product['_id'], product)
