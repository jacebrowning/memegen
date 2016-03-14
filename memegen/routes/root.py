from collections import OrderedDict

from flask import Blueprint, Response, render_template

from .. import __version__

from ._common import CHANGES_URL, route, get_tid


blueprint = Blueprint('root', __name__, url_prefix="/",
                      template_folder="../templates")


@blueprint.route("")
def get_index():
    return Response(render_template("index.html", ga_tid=get_tid()))


@blueprint.route("flask-api/static/js/default.js")
def get_javascript():
    return Response(render_template("js/default.js", ga_tid=get_tid()))


@blueprint.route("api")
def get():
    """Generate memes from templates."""
    data = OrderedDict()
    data['templates'] = route('templates.get', _external=True)
    data['aliases'] = route('aliases.get', _external=True)
    data['magic'] = route('magic.get', _external=True)
    data['version'] = __version__
    data['changes'] = CHANGES_URL
    return data


@blueprint.route("CHECK")
def handle_checks():
    """Return CHECK_OK for zero-downtime deployment.

    See: https://labnotes.org/zero-downtime-deploy-with-dokku

    """
    return "CHECK_OK"
