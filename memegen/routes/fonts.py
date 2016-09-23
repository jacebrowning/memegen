from flask import Blueprint, current_app as app
from flask_api import exceptions

from ._common import CONTRIBUTING_URL


blueprint = Blueprint('fonts', __name__, url_prefix="/api/fonts/")


@blueprint.route("")
def get():
    """Get a list of all available fonts."""
    return sorted(app.font_service.all())


@blueprint.route("", methods=['POST'])
def create_font():
    raise exceptions.PermissionDenied(CONTRIBUTING_URL)
