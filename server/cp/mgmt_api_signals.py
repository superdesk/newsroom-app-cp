from newsroom.signals import company_create


async def on_company_create(company, **kwargs):
    if not getattr(company, "auth_provider", None):
        company.auth_provider = "gip"


def init_app(app):
    company_create.connect(on_company_create)
