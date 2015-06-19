from collections import OrderedDict

from flask import Blueprint, current_app as app, request, url_for
from flask_api import exceptions


blueprint = Blueprint('templates', __name__, url_prefix="/templates/")


@blueprint.route("")
def get():
    """Get a list of all meme templates."""
    data = OrderedDict()
    for template in sorted(app.template_service.all()):
        url = url_for(".create", key=template.key, _external=True)
        data[template.name] = url
    return data


@blueprint.route("<key>", methods=['GET', 'POST'])
def create(key):
    """Generate a meme from a template."""
    if request.method == 'GET':
        template = app.template_service.find(key)
        path = template.default or "hello/world"
        url = url_for("links.get", key=key, path=path, _external=True)
        return dict(example=url)
    elif request.method == 'POST':
        # TODO: https://github.com/jacebrowning/memegen/issues/12
        raise exceptions.PermissionDenied("Feature not implemented.")
    else:  # pragma: no cover
        assert None
