from bson import ObjectId
from flask import Blueprint, jsonify
from newsroom.companies import CompaniesResource, CompaniesService
import superdesk

blueprint = Blueprint('companies', __name__)


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)


@blueprint.route('/api/companies/<_id>/products', methods=['GET', 'OPTIONS'])
def get_company_products(_id):
    products = superdesk.get_resource_service('products').find({'companies': ObjectId(_id)})
    return jsonify(list(products))
