from flask import Blueprint, current_app
from flask_api import exceptions


blueprint = Blueprint('fonts', __name__, url_prefix="/api/fonts/")


@blueprint.route("")
def get():
    """Get a list of all available fonts."""
    return sorted(current_app.font_service.all())


@blueprint.route("", methods=['POST'])
def create_font():
    raise exceptions.PermissionDenied(current_app.config['CONTRIBUTING_URL'])
