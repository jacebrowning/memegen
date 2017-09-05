from collections import OrderedDict

from flask import Blueprint, current_app

from .. import __version__

from ._utils import route


blueprint = Blueprint('root', __name__)


@blueprint.route("/api/")
def get():
    """Generate memes from templates."""
    data = OrderedDict()
    data['templates'] = route('templates.get', _external=True)
    data['fonts'] = route('fonts.get', _external=True)
    data['aliases'] = route('aliases.get', _external=True)
    data['search'] = route('search.get', _external=True)
    data['version'] = __version__
    data['changes'] = current_app.config['CHANGES_URL']
    return data


@blueprint.route("/CHECK")
def handle_checks():
    """Return CHECK_OK for zero-downtime deployment.

    See: https://labnotes.org/zero-downtime-deploy-with-dokku

    """
    return "CHECK_OK"
