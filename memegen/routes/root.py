from collections import OrderedDict

from flask import Blueprint, current_app as app, url_for, redirect, send_file

from ..domain import Image


blueprint = Blueprint('root', __name__, url_prefix="/")

GITHUB_BASE = "http://github.com/jacebrowning/memegen/blob/master/"


@blueprint.route("")
def get(**kwargs):
    """Generate memes from templates."""
    data = OrderedDict()
    data['templates'] = url_for("templates.get", _external=True)
    data['contributing'] = GITHUB_BASE + "CONTRIBUTING.md"
    return data


@blueprint.route("flask-api/static/js/default.js")
def get_javascript():
    return send_file("routes/default.js", mimetype='application/javascript')
