from flask import Blueprint, render_template
from newsroom.decorator import admin_only


blueprint = Blueprint("mgmt_api_docs", __name__)


@blueprint.route("/apidocs")
@admin_only
def mgmt_api_docs():
    return render_template("mgmt-apidocs.html")
