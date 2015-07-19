from collections import OrderedDict

from flask import Blueprint, url_for, send_file

from ._common import GITHUB_BASE, CONTRIBUTING


blueprint = Blueprint('root', __name__, url_prefix="/")


@blueprint.route("")
def get():
    """Generate memes from templates."""
    data = OrderedDict()
    data['templates'] = url_for("templates.get", _external=True)
    data['overview'] = url_for("overview.get", _external=True)
    data['source'] = GITHUB_BASE
    data['contributing'] = CONTRIBUTING
    return data


@blueprint.route("flask-api/static/js/default.js")
def get_javascript():
    return send_file("routes/default.js", mimetype='application/javascript')


@blueprint.route("CHECK")
def handle_checks():
    """Return CHECK_OK for zero-downtime deployment.

    See: https://labnotes.org/zero-downtime-deploy-with-dokku
    """
    return "CHECK_OK"
