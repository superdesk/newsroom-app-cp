from newsroom.products import ProductsResource, ProductsService
import superdesk


def init_app(app):
    ProductsResource.internal_resource = True
    ProductsResource.datasource['projection'] = {'companies': 0}
    superdesk.register_resource('products', ProductsResource, ProductsService, _app=app)
