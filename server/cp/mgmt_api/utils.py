import bson
import superdesk


def validate_product_refs(product_refs):
    products_service = superdesk.get_resource_service("products")
    product_ids = [bson.ObjectId(ref["_id"]) for ref in product_refs]
    products = list(
        products_service.get_from_mongo(req=None, lookup={"_id": {"$in": product_ids}})
    )
    products_by_id = {str(product["_id"]): product for product in products}

    for ref in product_refs:
        product = products_by_id.get(str(ref["_id"]))
        assert product is not None
        ref["section"] = product["product_type"]
