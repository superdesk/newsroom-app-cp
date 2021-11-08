from newsroom.companies import CompaniesResource, CompaniesService
import superdesk


def init_app(app):
    CompaniesResource.internal_resource = False
    CompaniesResource.public_methods = ["GET", "PATCH", "POST", "DELETE"]
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)
