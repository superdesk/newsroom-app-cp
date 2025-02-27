from newsroom.signals import company_create


async def on_company_create(company, **kwargs):
    company.setdefault("auth_provider", "gip")


def init_app(app):
    company_create.connect(on_company_create)
