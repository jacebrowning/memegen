from collections import OrderedDict

from flask import Blueprint, current_app as app, request, url_for
from flask_api import exceptions


blueprint = Blueprint('templates', __name__, url_prefix="/templates/")


@blueprint.route("")
def get():
    """Get a list of all meme templates."""
    data = OrderedDict()
    data['Insanity Wolf'] = url_for(".create", key='iw', _external=True)
    return data


@blueprint.route("<key>", methods=['GET', 'POST'])
def create(key):
    """Generate a meme from a template."""
    if request.method == 'GET':
        return dict(example=url_for("links.get", key=key, _external=True,
                                    top="hello", bottom="world"))
    elif request.method == 'POST':
        # TODO: https://github.com/jacebrowning/memegen/issues/12
        raise exceptions.PermissionDenied("Feature not implemented.")
    else:  # pragma: no cover
        assert None
