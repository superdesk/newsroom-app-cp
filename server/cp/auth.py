from typing import Optional
import flask
import logging
import google.oauth2.id_token

from flask_babel import gettext
from flask import current_app as app
from google.auth.transport import requests

from newsroom.types import AuthProviderType
from newsroom.auth import get_company, get_user_by_email
from newsroom.auth.utils import (
    sign_user_by_email,
    get_company_auth_provider,
    send_token,
)
from newsroom.auth.views import logout as _logout

from .password_reset_form import PasswordResetForm

TIMEOUT = 5

logger = logging.getLogger(__name__)
firebase_request_adapter = requests.Request()
blueprint = flask.Blueprint("cp.auth", __name__)


@blueprint.route("/auth_token")
def token():
    claims = None
    token = flask.request.args.get("token")
    if token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                token,
                audience=app.config["AUTH_FIREBASE_AUDIENCE"],
                request=firebase_request_adapter,
            )
        except ValueError as err:
            logger.error(err)
            flask.flash(gettext("User token is not valid"), "danger")
            return flask.redirect(flask.url_for("auth.login", token_error=1))

        email = claims["email"]
        return sign_user_by_email(
            email, auth_type=AuthProviderType.GOOGLE_OAUTH, validate_login_attempt=True
        )

    return flask.redirect(flask.url_for("auth.login"))


@blueprint.route("/logout")
def logout():
    _logout()
    return flask.redirect(flask.url_for("auth.login", logout=1))


@blueprint.route("/cp_reset_password_done")
def reset_password_confirmation():
    flask.flash(
        gettext("A reset password token has been sent to your email address."),
        "success",
    )
    return flask.redirect(flask.url_for("auth.login"))


@blueprint.route("/cp_reset_password", methods=["GET", "POST"])
def reset_password():
    form = PasswordResetForm()

    def render_reset_page(error_str: Optional[str] = None):
        if error_str is not None:
            flask.flash(error_str, "danger")

        return flask.render_template("cp_reset_password.html", form=form)

    if form.validate_on_submit():
        if form.email_sent.data is True:
            # Password reset was handled by firebase from the front-end
            return flask.redirect(flask.url_for("cp.auth.reset_password_confirmation"))

        # Password reset was not handled in the front-end, continue with standard password reset procedure
        user = get_user_by_email(form.email.data)
        if not user:
            return render_reset_page(gettext("User not found"))
        elif not user.get("is_enabled"):
            return render_reset_page(gettext("User not enabled"))

        company = get_company(user)
        auth_provider = get_company_auth_provider(company)

        if auth_provider["auth_type"] != AuthProviderType.PASSWORD.value:
            return render_reset_page(
                gettext(
                    "Password reset for your account is not supported through Newshub"
                )
            )

        # Send standard Newshub reset password email
        if not send_token(user, "reset_password"):
            return render_reset_page(
                gettext("An error occurred while sending reset password email")
            )

        return flask.redirect(flask.url_for("cp.auth.reset_password_confirmation"))

    return render_reset_page()
