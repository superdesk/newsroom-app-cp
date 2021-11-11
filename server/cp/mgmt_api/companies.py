from newsroom.companies import CompaniesResource, CompaniesService
import superdesk


def init_app(app):
    CompaniesResource.internal_resource = False
    superdesk.register_resource('companies', CompaniesResource, CompaniesService, _app=app)
