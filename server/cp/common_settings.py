from flask_babel import lazy_gettext

from newsroom.web.default_settings import AUTH_PROVIDERS
from newsroom.types import AuthProviderType

AUTH_PROVIDERS.extend([{
    "_id": "gip",
    "name": lazy_gettext("Google"),
    "auth_type": AuthProviderType.GOOGLE_OAUTH.value,
}, {
    "_id": "azure",
    "name": lazy_gettext("Azure"),
    "auth_type": AuthProviderType.SAML.value,
}])
