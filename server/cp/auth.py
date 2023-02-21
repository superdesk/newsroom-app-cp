import flask
import logging
import google.oauth2.id_token

from flask_babel import gettext
from google.auth.transport import requests
from newsroom.auth.utils import sign_user_by_email

TIMEOUT = 5

logger = logging.getLogger(__name__)
firebase_request_adapter = requests.Request()
blueprint = flask.Blueprint("cp.auth", __name__)


@blueprint.route("/auth_token")
def token():
    claims = None
    token = flask.request.cookies.get('token')
    if token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                token,
                audience="cp-identity",
                request=firebase_request_adapter,
            )
        except ValueError as err:
            logger.error(err)
            flask.flash(gettext("User token is not valid"), "danger")
            return flask.redirect(flask.url_for("auth.login", token_error=1))

        email = claims["email"]
        return sign_user_by_email(email)

    return flask.redirect(flask.url_for("auth.index"))


@blueprint.route("/logout")
def logout():
    flask.session.pop("user", None)
    flask.session.pop("name", None)
    flask.session.pop("user_type", None)
    resp = flask.redirect(flask.url_for("auth.login", logout=1))
    resp.delete_cookie("token")
    return resp


@blueprint.route("/reset_password_done")
def reset_password_confirmation():
    return flask.render_template("reset_password_confirmation.html")


@blueprint.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if flask.request.method == "POST":
        return flask.redirect(flask.url_for("cp.auth.reset_password_confirmation"))
    return flask.render_template("reset_password.html")
