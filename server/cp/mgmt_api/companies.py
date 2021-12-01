from bson.objectid import ObjectId
from flask import request
import newsroom
from newsroom.companies import CompaniesResource, CompaniesService
from newsroom.products.products import ProductsResource
from newsroom.utils import find_one
import superdesk


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)
    superdesk.register_resource('company_products', CompanyProductsResource, CompanyProductsService, _app=app)


class CompanyProductsResource(newsroom.Resource):
    endpoint_name = "company-product"
    url = 'companies/<regex("[a-f0-9]{24}"):companies>/products'
    item_url = r'regex("[a-f0-9]{24}")'
    resource_methods = ["GET", "POST"]
    item_methods = ["GET", "DELETE"]
    schema = {
        'product_ids': {
            'type': 'list',
            'nullable': True,
        },
    }
    datasource = {
        "source": "products",
        "projection": {
            name: 1
            for name in ProductsResource.schema.keys()
        }
    }


class CompanyProductsService(newsroom.Service):
    def get(self, req, lookup):
        company_id = lookup.pop("companies")
        lookup["companies"] = {"$in": [ObjectId(company_id)]}
        return super().get(req, lookup)

    def find_one(self, req, **lookup):
        lookup.pop("companies", None)
        return super().find_one(req, **lookup)

    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            product_ids = doc.pop('product_ids', [])
            for id in product_ids:
                product = find_one('products', _id=ObjectId(id))
                assert product
                product_companies = product.get('companies') or []
                company_id = ObjectId(request.view_args['companies'])
                if company_id not in product_companies:
                    product_companies.append(company_id)
                    superdesk.get_resource_service('products').system_update(
                        ObjectId(id), {"companies": product_companies}, product
                    )
                ids.append(id)
        return ids

    def delete(self, lookup):
        product = find_one('products', _id=lookup["_id"])
        assert product
        product_companies = [_id for _id in product["companies"] if str(_id) != lookup["companies"]]
        superdesk.get_resource_service('products').system_update(
            product["_id"], {"companies": product_companies}, product
        )
        return

    def on_fetched(self, doc):
        for item in doc["_items"]:
            self._fix_link(item)
        return super().on_fetched(doc)

    def on_fetched_item(self, doc):
        self._fix_link(doc)
        return super().on_fetched_item(doc)

    def _fix_link(self, item):
        company_id = request.view_args['companies']
        item["_links"]["self"]["href"] = f"companies/{company_id}/products/{item['_id']}"
