import newsroom
from newsroom.companies import CompaniesResource, CompaniesService
from newsroom.utils import query_resource
import superdesk
from superdesk.utils import ListCursor


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)

    endpoint_name = "company_products"
    service = CompanyProductsService(endpoint_name, backend=superdesk.get_backend())
    CompanyProductsResource(endpoint_name, app=app, service=service)


class CompanyProductsResource(newsroom.Resource):
    url = 'companies/<regex("[a-f0-9]{24}"):company_id>/products'
    resource_methods = ["GET"]


class CompanyProductsService(newsroom.Service):
    def get(self, req, lookup):
        products = query_resource('products', lookup={"is_enabled": True})
        company_products = []
        for product in products:
            if product.get('companies') and lookup['company_id'] in product.get('companies'):
                company_products.append(product)

        return ListCursor(company_products)
