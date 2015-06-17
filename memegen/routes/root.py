from collections import OrderedDict

from flask import Blueprint, current_app as app, url_for, redirect

from ..domain import Image


blueprint = Blueprint('root', __name__, url_prefix="/")


@blueprint.route("")
def get(**kwargs):
    """Generate memes from templates."""
    data = OrderedDict()
    data['templates'] = url_for("templates.get", _external=True)
    return data
