from bson.objectid import ObjectId
import newsroom
from flask import request
from newsroom.companies import CompaniesResource, CompaniesService
from newsroom.utils import query_resource
import superdesk
from superdesk.utils import ListCursor


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)
    superdesk.register_resource('company_products', CompanyProductsResource, CompanyProductsService, _app=app)


class CompanyProductsResource(newsroom.Resource):
    url = 'companies/<regex("[a-f0-9]{24}"):company_id>/products'
    resource_methods = ["GET", "POST"]
    schema = {
        'product_ids': {
            'type': 'list',
            'nullable': True,
        },
    }


class CompanyProductsService(newsroom.Service):
    def get(self, req, lookup):
        products = query_resource('products', lookup={"is_enabled": True})
        company_products = []
        for product in products:
            if product.get('companies') and lookup['company_id'] in product.get('companies'):
                company_products.append(product)

        return ListCursor(company_products)

    def create(self, docs, **kwargs):
        for doc in docs:
            product_ids = doc.pop('product_ids', [])
            if product_ids:
                return_response = []
                for id in product_ids:
                    product = query_resource('products', lookup={"_id": id})[0]
                    doc['companies'] = product.get('companies', [])
                    company_id = request.view_args['company_id']
                    if company_id not in doc['companies']:
                        doc['companies'].append(company_id)
                        superdesk.get_resource_service('products').patch(id=ObjectId(id), updates=doc)
                        return_response.append(id)
                return return_response
