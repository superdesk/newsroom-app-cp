from bson import ObjectId
from flask import Blueprint, jsonify, request
from newsroom.companies import CompaniesResource, CompaniesService
from newsroom.utils import get_entity_or_404
import superdesk

blueprint = Blueprint('companies', __name__)


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)


@blueprint.route('/api/companies/<_id>/products', methods=['GET', 'OPTIONS'])
def get_company_products(_id):
    """ Fetches the company products by given id """
    products = superdesk.get_resource_service('products').find({'companies': ObjectId(_id)})
    return jsonify(list(products)), 200


@blueprint.route('/api/companies/<product_id>/products', methods=['PATCH'])
def patch_company_products(product_id):
    """ Updates the company products by given id """
    get_entity_or_404(ObjectId(product_id), 'products')
    updates = request.get_json()
    superdesk.get_resource_service('products').patch(id=ObjectId(product_id), updates=updates)
    return jsonify({'success': True}), 200


@blueprint.route('/api/companies/<product_id>/products', methods=['DELETE'])
def delete_company_products(product_id):
    """ Deletes the company products by given id """
    get_entity_or_404(ObjectId(product_id), 'products')
    superdesk.get_resource_service('products').delete_action({'_id': ObjectId(product_id)})
    return jsonify({'success': True}), 200
