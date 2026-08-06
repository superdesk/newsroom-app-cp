"""Tests for the CP PR-Manager SSO / OIDC provider (cp/auth.py).

Scope: ONLY the CP-specific surface — the OIDC provider (authorize/token/PKCE),
email_verified enforcement, the Firebase re-check, and config fail-fast. NewsPro
user/company state, auth-provider gating and rate-limiting are covered upstream
(newsroom-core tests/core/test_auth.py, test_auth_providers.py) and not repeated.

Firebase is never contacted: verify_id_token / get_user are patched. Everything
else (PKCE, code store/expiry, redirect allowlist, client auth, Redis session)
runs for real.

NOTE (harness): cp/auth.py does real work at import — it reads the CP_OIDC_* /
FIREBASE_CONFIG env vars (raising if the required ones are missing), reads the JWK
file, and initializes a Firebase app. The block below sets that up before the
module is imported. If the `app`/`client` fixture registers cp.auth earlier than
this module is collected, move this block into server/tests/conftest.py.
"""

import base64
import hashlib
import importlib
import os
import secrets
from http.cookies import SimpleCookie
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest
from jwcrypto.jwk import JWK

# --- make cp.auth importable (env + JWK + patched firebase) ----------------- #
_JWK_PATH = Path(__file__).parent / "fixtures" / "oidc_test_jwk.json"
_JWK_PATH.parent.mkdir(exist_ok=True)
jwk = JWK.generate(kty="RSA", size=2048)
jwk["kid"] = "test-kid"
_JWK_PATH.write_text(jwk.export())

os.environ.setdefault("CP_OIDC_ISSUER", "https://newspro.test")
os.environ.setdefault("CP_OIDC_JWK", str(_JWK_PATH))
os.environ.setdefault("CP_OIDC_CLIENT_ID", "pr-manager")
os.environ.setdefault("CP_OIDC_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("CP_OIDC_REDIRECT_URI_LIST", "https://prmanager.test/callback")
os.environ.setdefault("FIREBASE_CONFIG", "unused-under-test")

# Firebase init/credential are patched so import needs no real service account.
mock.patch("firebase_admin.initialize_app", return_value=mock.MagicMock()).start()
mock.patch(
    "firebase_admin.credentials.Certificate", return_value=mock.MagicMock()
).start()

auth = importlib.import_module("cp.auth")

REDIRECT_URI = next(iter(auth.OIDC_REDIRECT_URI_LIST))
CLIENT_ID = auth.OIDC_CLIENT_ID
CLIENT_SECRET = auth.OIDC_CLIENT_SECRET
EMAIL = "user@example.com"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def fb_user(uid="uid-1", email=EMAIL, *, verified=True, disabled=False):
    user = mock.MagicMock()
    user.uid = uid
    user.email = email
    user.email_verified = verified
    user.disabled = disabled
    return user


def claims(uid="uid-1", email=EMAIL, *, verified=True):
    return {"uid": uid, "email": email, "email_verified": verified}


def pkce():
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


@pytest.fixture
def seed_user(app):
    """Create the NewsPro user the SSO flow signs in. ADAPT to your factory."""

    async def _seed(email=EMAIL):
        from newsroom.types import UserResourceModel  # noqa: PLC0415
        from newsroom.users.service import UsersService  # noqa: PLC0415

        await UsersService().create(
            [UserResourceModel(email=email, first_name="T", last_name="User")]
        )
        return email

    return _seed


@pytest.fixture(autouse=True)
async def register_cp_auth(app):
    async with app.app_context():
        auth.init_app(app)
    yield


async def login(client, *, uid="uid-1", email=EMAIL, verified=True):
    """Complete /firebase_auth_token; leaves the cp_session cookie on `client`."""
    user = mock.MagicMock(id="user-1")
    response = auth.Response(status=200)
    with (
        mock.patch.object(
            auth, "verify_id_token", return_value=claims(uid, email, verified=verified)
        ),
        mock.patch.object(
            auth, "get_user", return_value=fb_user(uid, email, verified=verified)
        ),
        mock.patch.object(
            auth,
            "sign_user_by_email",
            new=mock.AsyncMock(return_value=response),
        ),
        mock.patch.object(
            auth.UsersService,
            "get_by_email",
            new=mock.AsyncMock(return_value=user),
        ),
        mock.patch.object(
            auth,
            "get_user_or_none_from_request",
            return_value=user,
        ),
    ):
        return await client.get("/firebase_auth_token?token=fake")


def seed_cp_session(client, *, uid="uid-1", email=EMAIL, verified=True):
    session_id = "test-session"
    auth._update_cp_session(
        session_id,
        {
            "created_at": "0",
            "email": email,
            "uid": uid,
            "email_verified": "1" if verified else "0",
        },
    )
    client.set_cookie("localhost", auth.CP_SESSION_COOKIE_NAME, session_id, path="/")


async def get_code(
    client, *, challenge, redirect_uri=REDIRECT_URI, state="s1", scope="openid"
):
    with mock.patch.object(auth, "get_user", return_value=fb_user()):
        resp = await client.get(
            "/oidc/authorize",
            query_string={
                "response_type": "code",
                "client_id": CLIENT_ID,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            },
        )
    from urllib.parse import parse_qs, urlparse  # noqa: PLC0415

    return parse_qs(urlparse(resp.headers["Location"]).query)["code"][0]


async def exchange(
    client,
    *,
    code,
    verifier,
    redirect_uri=REDIRECT_URI,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
):
    with mock.patch.object(auth, "get_user", return_value=fb_user()):
        return await client.post(
            "/oidc/token",
            form={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": verifier,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )


def redirect_error(resp):
    location = resp.headers.get("Location", "")
    if not location:
        return None
    return parse_qs(urlparse(location).query).get("error", [None])[0]


def has_cp_cookie(resp):
    cookies = SimpleCookie()
    cookies.load(resp.headers.get("Set-Cookie", ""))
    return auth.CP_SESSION_COOKIE_NAME in cookies


# --------------------------------------------------------------------------- #
# 1. Happy path
# --------------------------------------------------------------------------- #
async def test_full_round_trip(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    verifier, challenge = pkce()
    code = await get_code(client, challenge=challenge)
    resp = await exchange(client, code=code, verifier=verifier)
    assert resp.status_code == 200
    body = await resp.get_json()
    assert body["access_token"] and body["id_token"]


# --------------------------------------------------------------------------- #
# 2. Firebase login — /firebase_auth_token  (CP-specific claim validation)
# --------------------------------------------------------------------------- #
async def test_login_missing_token(client):
    resp = await client.get("/firebase_auth_token")
    assert not has_cp_cookie(resp)


async def test_login_invalid_token(client):
    with mock.patch.object(auth, "verify_id_token", side_effect=Exception("bad")):
        resp = await client.get("/firebase_auth_token?token=fake")
    assert not has_cp_cookie(resp)


async def test_login_unverified_email_rejected(client, seed_user):
    await seed_user()
    resp = await login(client, verified=False)
    assert not has_cp_cookie(resp)


async def test_login_missing_email_or_uid(client):
    with mock.patch.object(
        auth, "verify_id_token", return_value={"email_verified": True}
    ):
        resp = await client.get("/firebase_auth_token?token=fake")
    assert not has_cp_cookie(resp)


# NOTE: unknown NewsPro user / disabled user / disabled company / not-approved are
# handled by sign_user_by_email and covered upstream (test_auth.py) — not here.


# --------------------------------------------------------------------------- #
# 3. OIDC authorize
# --------------------------------------------------------------------------- #
async def test_authorize_missing_redirect_uri(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    resp = await client.get(
        "/oidc/authorize",
        query_string={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "scope": "openid",
        },
    )
    assert resp.status_code >= 400


async def test_authorize_disallowed_redirect_uri(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    _, challenge = pkce()
    resp = await client.get(
        "/oidc/authorize",
        query_string={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": "https://evil.test/cb",
            "scope": "openid",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
    )
    assert "evil.test" not in resp.headers.get("Location", "")


async def test_authorize_missing_pkce(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    resp = await client.get(
        "/oidc/authorize",
        query_string={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "openid",
        },
    )
    assert redirect_error(resp) is not None


async def test_authorize_missing_openid_scope(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    _, challenge = pkce()
    resp = await client.get(
        "/oidc/authorize",
        query_string={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "profile",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
    )
    assert redirect_error(resp) == "invalid_scope"


async def test_authorize_requires_session(client):
    _, challenge = pkce()
    resp = await client.get(
        "/oidc/authorize",
        query_string={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "openid",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
    )
    assert redirect_error(resp) == "login_required"


# --------------------------------------------------------------------------- #
# 4. OIDC token exchange — /oidc/token  (SECURITY-CRITICAL)
# --------------------------------------------------------------------------- #
async def test_token_wrong_code_verifier_rejected(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    _, challenge = pkce()
    code = await get_code(client, challenge=challenge)
    wrong, _ = pkce()
    resp = await exchange(client, code=code, verifier=wrong)
    assert resp.status_code >= 400


async def test_token_missing_code_verifier_rejected(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    _, challenge = pkce()
    code = await get_code(client, challenge=challenge)
    resp = await exchange(client, code=code, verifier="")
    assert resp.status_code >= 400


async def test_token_code_is_single_use(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    verifier, challenge = pkce()
    code = await get_code(client, challenge=challenge)
    assert (await exchange(client, code=code, verifier=verifier)).status_code == 200
    assert (await exchange(client, code=code, verifier=verifier)).status_code >= 400


async def test_token_bad_client_secret_rejected(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    verifier, challenge = pkce()
    code = await get_code(client, challenge=challenge)
    resp = await exchange(client, code=code, verifier=verifier, client_secret="wrong")
    assert resp.status_code >= 400


@pytest.mark.skipif(
    len(auth.OIDC_REDIRECT_URI_LIST) < 2, reason="need 2 allowed redirect URIs"
)
async def test_token_redirect_uri_must_match(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    uris = list(auth.OIDC_REDIRECT_URI_LIST)
    verifier, challenge = pkce()
    code = await get_code(client, challenge=challenge, redirect_uri=uris[0])
    resp = await exchange(client, code=code, verifier=verifier, redirect_uri=uris[1])
    assert resp.status_code >= 400


# --------------------------------------------------------------------------- #
# 5. Live re-validation of the *Firebase* user
# (NewsPro is_enabled/is_approved is upstream; here we test _is_valid_firebase_user)
# --------------------------------------------------------------------------- #
async def test_session_rejected_when_firebase_user_disabled(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    with mock.patch.object(auth, "get_user", return_value=fb_user(disabled=True)):
        resp = await client.get("/cp_session")
    assert resp.status_code in {301, 302, 401}


async def test_session_rejected_when_firebase_user_deleted(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    with mock.patch.object(auth, "get_user", side_effect=Exception("not found")):
        resp = await client.get("/cp_session")
    assert resp.status_code in {301, 302, 401}


async def test_session_rejected_when_email_verified_revoked(client, seed_user):
    await seed_user()
    seed_cp_session(client)
    with mock.patch.object(auth, "get_user", return_value=fb_user(verified=False)):
        resp = await client.get("/cp_session")
    assert resp.status_code in {301, 302, 401}


# --------------------------------------------------------------------------- #
# 6. Configuration / startup — current behavior
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("missing", "expect_oidc_enabled"),
    [
        ("CP_OIDC_ISSUER", False),
        ("CP_OIDC_JWK", False),
        ("FIREBASE_CONFIG", True),
    ],
)
def test_missing_required_env_does_not_raise_and_disables_feature(
    monkeypatch, missing, expect_oidc_enabled
):
    original_value = os.environ.get(missing)
    monkeypatch.delenv(missing, raising=False)
    reloaded = importlib.reload(auth)

    if missing in {"CP_OIDC_ISSUER", "CP_OIDC_JWK"}:
        assert reloaded.IS_OIDC_ENABLED is expect_oidc_enabled
        assert reloaded.oidc_signing_key is None
    else:
        assert reloaded.firebase_app is None

    if original_value is not None:
        os.environ[missing] = original_value
    else:
        os.environ.pop(missing, None)
    importlib.reload(auth)


# --------------------------------------------------------------------------- #
# 7. Endpoint registration — smoke only (EndpointGroup mechanism is upstream)
# --------------------------------------------------------------------------- #
async def test_cp_routes_are_registered(client):
    for path in (
        "/firebase_auth_token",
        "/cp_session",
        "/oidc/.well-known/openid-configuration",
    ):
        resp = await client.get(path)
        assert resp.status_code != 404
