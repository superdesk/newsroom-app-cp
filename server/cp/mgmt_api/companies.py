from bson.objectid import ObjectId
from flask import request, current_app as app

import newsroom
from newsroom.companies import CompaniesResource, CompaniesService
from newsroom.companies.views import get_errors_company
from newsroom.products.products import ProductsResource
from newsroom.products.views import get_product_ref
from newsroom.utils import find_one
import superdesk
from superdesk.errors import SuperdeskApiError


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource(
        "companies", CPCompaniesResource, CPCompaniesService, _app=app
    )
    superdesk.register_resource(
        "company_products", CompanyProductsResource, CompanyProductsService, _app=app
    )


class CPCompaniesResource(CompaniesResource):
    """
    CP Companies Schema
    """

    schema = {
        **CompaniesResource.schema,
        "country": {"type": "string", "default": "CAN"},
    }


class CPCompaniesService(CompaniesService):
    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            errors = get_errors_company(doc)
            if errors:
                message = "invalid ip address"
                raise SuperdeskApiError.badRequestError(
                    message=message, payload=message
                )

    def on_created(self, docs):
        super().on_created(docs)
        for doc in docs:
            app.cache.set(str(doc["_id"]), doc)

    def on_update(self, updates, original):
        super().on_update(updates, original)
        app.cache.delete(str(original["_id"]))

    def on_delete(self, doc):
        super().on_delete(doc)
        app.cache.delete(str(doc["_id"]))


class CompanyProductsResource(newsroom.Resource):
    endpoint_name = "company-product"
    url = 'companies/<regex("[a-f0-9]{24}"):companies>/products'
    resource_methods = ["GET", "POST"]
    schema = {
        "product": {
            "type": "objectid",
            "required": True,
        },
        "seats": {
            "type": "number",
        },
        "link": {"type": "boolean", "nullable": False},
    }
    datasource = {
        "source": "products",
        "projection": {
            name: 1 for name in ProductsResource.schema.keys() if name != "companies"
        },
    }


def get_company():
    company = find_one("companies", _id=ObjectId(request.view_args["companies"]))
    assert company
    return company


def get_company_products(company):
    return company.get("products") or []


class CompanyProductsService(newsroom.Service):
    def get(self, req, lookup):
        self.company = get_company()
        company_products = get_company_products(self.company)
        lookup["_id"] = {"$in": [p["_id"] for p in company_products]}
        lookup.pop("companies", None)
        return super().get(req, lookup)

    def find_one(self, req, **lookup):
        lookup.pop("companies", None)
        return super().find_one(req, **lookup)

    def create(self, docs, **kwargs):
        ids = []
        for doc in docs:
            id = doc.pop("product")
            link = doc.pop("link")
            product = find_one("products", _id=ObjectId(id))
            company = get_company()
            assert product
            company_products = [
                p for p in get_company_products(company) if p["_id"] != product["_id"]
            ]
            if link:
                company_products.append(get_product_ref(product, doc.get("seats")))
            superdesk.get_resource_service("companies").system_update(
                company["_id"], {"products": company_products}, company
            )
            ids.append(id)
        return ids

    def on_fetched(self, doc):
        for item in doc["_items"]:
            self._fix_link(item)
            if (
                hasattr(self, "company")
                and self.company
                and self.company.get("products")
            ):
                for product_ref in self.company["products"]:
                    if product_ref["_id"] == item["_id"]:
                        item["seats"] = product_ref["seats"]
                        break
        return super().on_fetched(doc)

    def on_fetched_item(self, doc):
        self._fix_link(doc)
        return super().on_fetched_item(doc)

    def _fix_link(self, item):
        company_id = request.view_args["companies"]
        item["_links"]["self"][
            "href"
        ] = f"companies/{company_id}/products/{item['_id']}"
