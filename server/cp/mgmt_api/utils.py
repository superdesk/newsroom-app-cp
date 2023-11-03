import superdesk


def validate_product_refs(products):
    products_service = superdesk.get_resource_service("products")
    for product_spec in products:
        product = products_service.find_one(req=None, _id=product_spec["_id"])
        assert product is not None and product["product_type"] == product_spec.get(
            "section"
        ), (
            f"invalid product type for product {product_spec['_id']}, should be {product['product_type']}"
            if product
            else f"unknown product {product_spec['_id']}"
        )
