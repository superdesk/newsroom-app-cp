from newsroom.products import ProductsResource, ProductsService
import superdesk


def init_app(app):
    ProductsResource.internal_resource = False
    superdesk.register_resource('products', ProductsResource, ProductsService, _app=app)
