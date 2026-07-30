from base64 import b64decode, urlsafe_b64encode
from datetime import datetime, timedelta
from hashlib import sha256
from json import dumps, loads
from logging import INFO, getLogger
from os import environ
from pathlib import Path
from re import compile
from secrets import compare_digest
from time import time
from typing import cast
from urllib.parse import urlencode
from uuid import uuid4

from authlib.jose import jwt
from firebase_admin import initialize_app as initialize_firebase_app
from firebase_admin.auth import verify_id_token
from firebase_admin.credentials import Certificate as FirebaseCertificate
from flask import Response
from jwcrypto.jwk import JWK
from newsroom.auth.utils import (
    get_current_request,
    get_user_or_none_from_request,
    sign_user_by_email,
)
from newsroom.flask import flash
from newsroom.types import AuthProviderType
from newsroom.users.service import UsersService
from quart_babel import gettext
from redis import Redis
from superdesk.core import get_current_async_app
from superdesk.core.types import Request
from superdesk.core.web import EndpointGroup
from superdesk.flask import url_for
from werkzeug.http import parse_cookie

PKCE_CODE_VERIFIER_RE = compile(r"^[A-Za-z0-9._~-]{43,128}$")
PKCE_S256_CODE_CHALLENGE_RE = compile(r"^[A-Za-z0-9_-]{43}$")

CP_SESSION_COOKIE_NAME = "cp_session"
SESSION_EXPIRY = timedelta(days=1)
REFRESH_THRESHOLD = timedelta(minutes=5)
OIDC_AUTH_CODE_EXPIRY = timedelta(minutes=2)
OIDC_ACCESS_TOKEN_EXPIRY = timedelta(minutes=15)
OIDC_ID_TOKEN_EXPIRY = timedelta(minutes=5)
OIDC_SCOPES = {"openid", "profile", "email"}
OIDC_JWK = environ.get("CP_OIDC_JWK")
OIDC_CLIENT_ID = environ.get("CP_OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = environ.get("CP_OIDC_CLIENT_SECRET")
OIDC_ISSUER = environ.get("CP_OIDC_ISSUER")
OIDC_REDIRECT_URI_LIST = {
    uri for uri in environ.get("CP_OIDC_REDIRECT_URI_LIST", "").split(",") if uri
}
FIREBASE_CONFIG = environ.get("FIREBASE_CONFIG")

if not OIDC_JWK:
    raise Exception("CP_OIDC_JWK environment variable must be set")
if not FIREBASE_CONFIG:
    raise Exception("FIREBASE_CONFIG environment variable must be set")

blueprint = EndpointGroup("cp_auth", __name__)
logger = getLogger(__name__)
logger.setLevel(INFO)

firebase_app = initialize_firebase_app(credential=FirebaseCertificate(FIREBASE_CONFIG))

oidc_key = Path(OIDC_JWK).read_text()
oidc_signing_key = JWK.from_json(oidc_key)


@blueprint.endpoint("/firebase_auth_token", auth=False)
async def firebase_auth_token(args, params, request: Request):
    token = request.get_url_arg("token")
    if not token:
        await flash(gettext("User token is not valid"), "danger")
        return request.redirect(url_for("auth.login", token_error=1))

    try:
        claims = verify_id_token(token, firebase_app)
    except Exception as e:
        logger.error(f"Failed to verify token: {e}")
        await flash(gettext("User token is not valid"), "danger")
        return request.redirect(url_for("auth.login", token_error=1))

    email = claims["email"]
    uid = claims["uid"]

    response = await sign_user_by_email(
        email,
        auth_type=AuthProviderType.FIREBASE,
        validate_login_attempt=True,
    )

    user = await UsersService().get_by_email(email)
    logged_in_user = get_user_or_none_from_request(request)
    if user is None or logged_in_user is None or logged_in_user.id != user.id:
        return response

    session_id = str(uuid4())

    _update_cp_session(
        session_id,
        {
            "created_at": str(datetime.now().timestamp()),
            "email": email,
            "uid": uid,
        },
    )
    _set_cp_cookie(response, request, session_id)
    return response


@blueprint.endpoint("/cp_session")
def session_status(args, params, request: Request):
    session_id = _get_cp_session_cookie(request)
    if not session_id:
        return {}, 401

    session_data = _get_valid_cp_session_data(session_id)
    if not session_data:
        return {}, 401

    return {}, 200


def _get_cp_session_cookie(request: Request):
    return parse_cookie(request.get_header("Cookie")).get(CP_SESSION_COOKIE_NAME)


def _update_cp_session(session_id: str, data: dict[str, str] | None = None) -> None:
    key = _get_redis_key(session_id)
    pipe = _get_redis().pipeline()
    pipe.hset(
        key, mapping={**(data or {}), "updated_at": str(datetime.now().timestamp())}
    )
    pipe.expire(key, int(SESSION_EXPIRY.total_seconds()))
    pipe.execute()


def _set_cp_cookie(response: Response, request: Request, session_id: str) -> None:
    response.set_cookie(
        CP_SESSION_COOKIE_NAME,
        session_id,
        expires=datetime.now() + SESSION_EXPIRY,
        httponly=True,
        secure=_is_secure_request(request),
        samesite="Lax",
        path="/",
    )


def _get_redis() -> Redis:
    return get_current_async_app().wsgi.redis


def _get_redis_key(session_id: str) -> str:
    return f"{CP_SESSION_COOKIE_NAME}:{session_id}"


def _get_session_data_from_redis(session_id: str) -> dict[str, str]:
    value = cast(dict[bytes, bytes], _get_redis().hgetall(_get_redis_key(session_id)))
    return {k.decode("utf-8"): v.decode("utf-8") for k, v in value.items()}


def _get_valid_cp_session_data(session_id: str | None) -> dict[str, str] | None:
    if not session_id:
        return None

    session_data = _get_session_data_from_redis(session_id)
    if not session_data or "uid" not in session_data:
        return None

    return session_data


def _is_secure_request(request: Request) -> bool:
    forwarded_proto = request.get_header("X-Forwarded-Proto")
    if forwarded_proto:
        return forwarded_proto.split(",", 1)[0].strip().lower() == "https"

    return request.url.startswith("https")


@blueprint.endpoint("/oidc/.well-known/openid-configuration", auth=False)
def oidc_openid_configuration(args, params, request: Request):
    issuer = _get_oidc_issuer(request)
    return {
        "authorization_endpoint": f"{issuer}/oidc/authorize",
        "code_challenge_methods_supported": ["S256"],
        "grant_types_supported": ["authorization_code"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "issuer": issuer,
        "jwks_uri": f"{issuer}/oidc/jwks.json",
        "response_types_supported": ["code"],
        "scopes_supported": sorted(OIDC_SCOPES),
        "subject_types_supported": ["public"],
        "token_endpoint": f"{issuer}/oidc/token",
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
        ],
        "userinfo_endpoint": f"{issuer}/oidc/userinfo",
    }, 200


@blueprint.endpoint("/oidc/jwks.json", auth=False)
def oidc_jwks(args, params, request: Request):
    return {"keys": [loads(oidc_signing_key.export_public())]}, 200


def _validate_pkce_challenge(
    code_challenge: str | None,
    code_challenge_method: str | None,
) -> str | None:
    if not code_challenge:
        return "code_challenge is required"
    if code_challenge_method != "S256":
        return "code_challenge_method must be S256"
    if not PKCE_S256_CODE_CHALLENGE_RE.match(code_challenge):
        return "code_challenge is invalid"
    return None


def _is_pkce_verifier_valid(
    code_verifier: str | None,
    code_challenge: str | None,
) -> bool:
    if not code_verifier or not code_challenge:
        return False
    if not PKCE_CODE_VERIFIER_RE.match(code_verifier):
        return False

    digest = sha256(code_verifier.encode("ascii")).digest()
    computed = urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return compare_digest(computed, code_challenge)


@blueprint.endpoint("/oidc/authorize", methods=["GET"], auth=False)
def oidc_authorize(args, params, request: Request):
    client_id = request.get_url_arg("client_id")
    redirect_uri = request.get_url_arg("redirect_uri")
    response_type = request.get_url_arg("response_type")
    scope = request.get_url_arg("scope") or ""
    state = request.get_url_arg("state")
    nonce = request.get_url_arg("nonce")
    code_challenge = request.get_url_arg("code_challenge")
    code_challenge_method = request.get_url_arg("code_challenge_method")

    if not redirect_uri:
        return {
            "error": "invalid_request",
            "error_description": "redirect_uri is required",
        }, 400
    if not _is_redirect_uri_allowed(redirect_uri):
        return {
            "error": "invalid_redirect_uri",
            "error_description": "redirect uri is not allowed",
        }, 400
    if response_type != "code":
        return _oidc_redirect_error(
            redirect_uri, "unsupported_response_type", state=state
        )
    if "openid" not in scope.split():
        return _oidc_redirect_error(
            redirect_uri, "invalid_scope", "openid scope is required", state=state
        )
    if not _is_oidc_client_allowed(client_id):
        return _oidc_redirect_error(redirect_uri, "unauthorized_client", state=state)

    pkce_error = _validate_pkce_challenge(code_challenge, code_challenge_method)
    if pkce_error:
        return _oidc_redirect_error(
            redirect_uri,
            "invalid_request",
            pkce_error,
            state=state,
        )

    session_id = _get_cp_session_cookie(request)
    session_data = _get_valid_cp_session_data(session_id)
    if not session_id or not session_data:
        return _oidc_redirect_error(redirect_uri, "login_required", state=state)

    code = str(uuid4())
    _store_oidc_authorization_code(
        code,
        {
            "client_id": client_id or "",
            "nonce": nonce or "",
            "redirect_uri": redirect_uri,
            "scope": scope,
            "session_id": session_id,
            "sub": session_data["uid"],
            "code_challenge": code_challenge or "",
            "code_challenge_method": code_challenge_method or "",
        },
    )
    return request.redirect(_append_query_params(redirect_uri, code=code, state=state))


@blueprint.endpoint("/oidc/token", methods=["POST"], auth=False)
async def oidc_token(args, params, request: Request):
    form = await request.get_form()
    code = form.get("code")
    grant_type = form.get("grant_type")
    redirect_uri = form.get("redirect_uri")
    client_id = form.get("client_id")
    client_secret = form.get("client_secret")
    code_verifier = form.get("code_verifier")

    if grant_type != "authorization_code":
        return _oidc_json_response(
            {
                "error": "unsupported_grant_type",
                "error_description": "Only authorization_code is supported",
            },
            status=400,
        )

    basic_client_id, basic_client_secret = _parse_basic_auth(request)
    client_id = client_id or basic_client_id
    client_secret = client_secret or basic_client_secret

    if not _is_oidc_client_authenticated(client_id, client_secret):
        return _oidc_json_response({"error": "invalid_client"}, status=401)

    code_data = _pop_oidc_authorization_code(code)
    if not code_data:
        return _oidc_json_response({"error": "invalid_grant"}, status=400)
    if code_data.get("client_id") != (client_id or ""):
        return _oidc_json_response({"error": "invalid_grant"}, status=400)
    if code_data.get("redirect_uri") != (redirect_uri or ""):
        return _oidc_json_response({"error": "invalid_grant"}, status=400)
    if not _is_pkce_verifier_valid(
        code_verifier,
        code_data.get("code_challenge"),
    ):
        return _oidc_json_response({"error": "invalid_grant"}, status=400)

    session_data = _get_valid_cp_session_data(code_data.get("session_id"))
    if not session_data:
        return _oidc_json_response({"error": "invalid_grant"}, status=400)

    claims = _build_oidc_claims(
        request,
        session_data,
        audience=code_data.get("client_id", ""),
        nonce=code_data.get("nonce"),
    )
    access_token = str(uuid4())
    _store_oidc_access_token(access_token, claims)

    return _oidc_json_response(
        {
            "access_token": access_token,
            "expires_in": int(OIDC_ACCESS_TOKEN_EXPIRY.total_seconds()),
            "id_token": _encode_oidc_id_token(claims),
            "scope": code_data.get("scope", "openid"),
            "token_type": "Bearer",
        }
    )


@blueprint.endpoint("/oidc/userinfo", methods=["GET"], auth=False)
def oidc_userinfo(args, params, request: Request):
    token = _get_bearer_token(request)
    if not token:
        return _oidc_json_response({"error": "invalid_token"}, status=401)

    claims = _get_oidc_access_token_data(token)
    if not claims:
        return _oidc_json_response({"error": "invalid_token"}, status=401)

    return _oidc_json_response(
        {
            "email": claims.get("email"),
            "email_verified": bool(claims.get("email")),
            "name": claims.get("name") or claims["sub"],
            "preferred_username": claims.get("email") or claims["sub"],
            "sub": claims["sub"],
        }
    )


def _get_oidc_redis_key(kind: str, token: str) -> str:
    return f"{CP_SESSION_COOKIE_NAME}:oidc:{kind}:{token}"


def _store_oidc_authorization_code(code: str, data: dict[str, str]) -> None:
    key = _get_oidc_redis_key("code", code)
    pipe = _get_redis().pipeline()
    pipe.hset(key, mapping=data)
    pipe.expire(key, int(OIDC_AUTH_CODE_EXPIRY.total_seconds()))
    pipe.execute()


def _pop_oidc_authorization_code(code: str | None) -> dict[str, str] | None:
    if not code:
        return None

    key = _get_oidc_redis_key("code", code)
    redis = _get_redis()
    pipe = redis.pipeline()
    pipe.hgetall(key)
    pipe.delete(key)
    data, _ = pipe.execute()
    if not data:
        return None

    return {k.decode("utf-8"): v.decode("utf-8") for k, v in data.items()}


def _store_oidc_access_token(token: str, claims: dict[str, str | int | bool]) -> None:
    key = _get_oidc_redis_key("access_token", token)
    mapping = {k: dumps(v) for k, v in claims.items()}
    pipe = _get_redis().pipeline()
    pipe.hset(key, mapping=mapping)
    pipe.expire(key, int(OIDC_ACCESS_TOKEN_EXPIRY.total_seconds()))
    pipe.execute()


def _get_oidc_access_token_data(token: str) -> dict[str, str | int | bool] | None:
    value = cast(
        dict[bytes, bytes],
        _get_redis().hgetall(_get_oidc_redis_key("access_token", token)),
    )
    if not value:
        return None

    return {k.decode("utf-8"): loads(v.decode("utf-8")) for k, v in value.items()}


def _get_oidc_issuer(request: Request) -> str:
    return OIDC_ISSUER or request.url.rsplit("/oidc/", 1)[0]


def _is_oidc_client_allowed(client_id: str | None) -> bool:
    if not OIDC_CLIENT_ID or not client_id:
        return False
    return compare_digest(client_id, OIDC_CLIENT_ID)


def _is_redirect_uri_allowed(redirect_uri: str | None) -> bool:
    return redirect_uri in OIDC_REDIRECT_URI_LIST


def _is_oidc_client_authenticated(
    client_id: str | None, client_secret: str | None
) -> bool:
    if (
        not OIDC_CLIENT_ID
        or not OIDC_CLIENT_SECRET
        or not client_id
        or not client_secret
    ):
        return False

    id_matches = compare_digest(client_id, OIDC_CLIENT_ID)
    secret_matches = compare_digest(client_secret, OIDC_CLIENT_SECRET)
    return id_matches and secret_matches


def _parse_basic_auth(request: Request) -> tuple[str | None, str | None]:
    auth_header = (request.get_header("Authorization") or "").strip()
    if not auth_header.startswith("Basic "):
        return None, None

    try:
        decoded = b64decode(auth_header.split(" ", 1)[1]).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        return None, None

    return username, password


def _get_bearer_token(request: Request) -> str | None:
    auth_header = (request.get_header("Authorization") or "").strip()
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def _build_oidc_claims(
    request: Request,
    session_data: dict[str, str],
    audience: str,
    nonce: str | None = None,
) -> dict[str, str | int | bool]:
    now = int(time())
    claims: dict[str, str | int | bool] = {
        "aud": audience,
        "email": session_data.get("email", ""),
        "email_verified": bool(session_data.get("email")),
        "exp": now + int(OIDC_ID_TOKEN_EXPIRY.total_seconds()),
        "iat": now,
        "iss": _get_oidc_issuer(request),
        "name": session_data.get("email") or session_data["uid"],
        "sub": session_data["uid"],
    }
    if nonce:
        claims["nonce"] = nonce
    return claims


def _encode_oidc_id_token(claims: dict[str, str | int | bool]) -> str:
    header = {"alg": "RS256", "kid": oidc_signing_key["kid"], "typ": "JWT"}
    token = jwt.encode(
        header, claims, oidc_signing_key.export_to_pem(private_key=True, password=None)
    )
    return token.decode("utf-8")


def _append_query_params(url: str, **params: str | None) -> str:
    filtered_params = {k: v for k, v in params.items() if v is not None}
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urlencode(filtered_params)}"


def _oidc_redirect_error(
    redirect_uri: str,
    error: str,
    error_description: str | None = None,
    state: str | None = None,
):
    return Response(
        status=302,
        headers={
            "Location": _append_query_params(
                redirect_uri,
                error=error,
                error_description=error_description,
                state=state,
            )
        },
    )


def _oidc_json_response(data: dict[str, object], status: int = 200) -> Response:
    return Response(
        dumps(data),
        status=status,
        mimetype="application/json",
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )


def init_refresh_session_hook(app):
    @app.after_request
    async def refresh_cp_session(response):
        request = get_current_request()
        session_id = _get_cp_session_cookie(request)
        if not session_id:
            return response

        session_data = _get_session_data_from_redis(session_id)
        if not session_data or "updated_at" not in session_data:
            return response

        last_updated = datetime.now().timestamp() - float(session_data["updated_at"])
        if last_updated > REFRESH_THRESHOLD.total_seconds():
            _update_cp_session(session_id)
            _set_cp_cookie(response, request, session_id)

        return response


def init_app(app):
    init_refresh_session_hook(app)
    get_current_async_app().wsgi.register_endpoint(blueprint)
