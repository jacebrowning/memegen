from collections import OrderedDict

from flask import Blueprint, current_app as app, request, redirect
from flask_api import exceptions

from ._common import CONTRIBUTING_URL, route


blueprint = Blueprint('templates', __name__, url_prefix="/templates/")


@blueprint.route("")
def get():
    """Get a list of all meme templates."""
    data = OrderedDict()
    for template in sorted(app.template_service.all()):
        url = route('.create', key=template.key, _external=True)
        data[template.name] = url
    return data


@blueprint.route("", methods=['POST'])
def create_template():
    raise exceptions.PermissionDenied(CONTRIBUTING_URL)


@blueprint.route("<key>", methods=['GET', 'POST'], endpoint='create')
def create_meme(key):
    """Generate a meme from a template."""
    if request.method == 'GET':
        template = app.template_service.find(key)
        if template.key != key:
            return redirect(route('.create', key=template.key))

        data = OrderedDict()
        data['name'] = template.name
        data['description'] = template.link
        data['aliases'] = sorted(template.aliases + [template.key])
        data['styles'] = template.styles
        data['example'] = route('links.get', key=key,
                                path=template.sample_path, _external=True)
        return data

    elif request.method == 'POST':
        # TODO: https://github.com/jacebrowning/memegen/issues/12
        raise exceptions.PermissionDenied("Feature not implemented.")

    else:  # pragma: no cover
        assert None


@blueprint.route("<key>/<path:path>")
def get_meme_with_path(key, path):
    """Redirect if any additional path is provided."""
    template = app.template_service.find(key)
    return redirect("/{}/{}".format(template.key, path))
