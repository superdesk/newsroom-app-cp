import flask
import logging
import superdesk
import google.oauth2.id_token

from flask_babel import gettext
from superdesk.utc import utcnow
from google.auth.transport import requests

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
        users = superdesk.get_resource_service("users")
        user = users.find_one(req=None, email=email)
        if user is None:
            flask.flash("User not found", "danger")
            return flask.redirect(flask.url_for("auth.login", user_error=1))

        users.system_update(user["_id"], {
            "is_validated": True,  # in case user was not validated before set it now
            "last_active": utcnow(),
        }, user)

        # Set flask session information
        flask.session["user"] = str(user["_id"])
        flask.session["name"] = "{} {}".format(user.get("first_name"), user.get("last_name"))
        flask.session["user_type"] = user["user_type"]
        return flask.redirect(flask.url_for("wire.index"))

    return flask.redirect(flask.url_for("auth.index"))


@blueprint.route("/logout")
def logout():
    flask.session.pop("user", None)
    flask.session.pop("name", None)
    flask.session.pop("user_type", None)
    resp = flask.redirect(flask.url_for("auth.login", logout=1))
    resp.delete_cookie("token")
    return resp


def init_app(_app):
    _app.view_functions['auth.logout'] = logout
