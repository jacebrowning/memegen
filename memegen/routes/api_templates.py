from collections import OrderedDict

from flask import Blueprint, current_app, request, redirect
from flask_api import exceptions
from webargs import fields

from ..domain import Text

from ._parser import parser
from ._utils import route


blueprint = Blueprint('templates', __name__, url_prefix="/api/templates/")

OPTIONS = {
    'top': fields.Str(missing=""),
    'bottom': fields.Str(missing=""),
    '_redirect': fields.Bool(load_from='redirect', missing=True),
    '_masked': fields.Bool(load_from='masked', missing=False),
}


@blueprint.route("")
def get():
    """Get a list of all meme templates."""
    data = OrderedDict()
    for template in sorted(current_app.template_service.all()):
        url = route('.create', key=template.key, _external=True)
        data[template.name] = url
    return data


@blueprint.route("", methods=['POST'])
def create_template():
    raise exceptions.PermissionDenied(current_app.config['CONTRIBUTING_URL'])


@blueprint.route("<key>", methods=['GET', 'POST'], endpoint='create')
@parser.use_kwargs(OPTIONS)
def create_meme(key, top, bottom, _redirect, _masked):
    """Generate a meme from a template."""
    if request.method == 'GET':
        template = current_app.template_service.find(key)
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
        if top or bottom:
            text = Text([top, bottom], translate_spaces=False)
        else:
            text = Text("_")

        if _masked:
            code = current_app.link_service.encode(key, text.path)
            url = route('image.get_encoded', code=code, _external=True)
        else:
            url = route('image.get', key=key, path=text.path, _external=True)

        if _redirect:
            return redirect(url, 303)
        else:
            return dict(href=url)

    else:  # pragma: no cover
        assert None


@blueprint.route("<key>/<path:path>")
def get_meme_with_path(key, path):
    """Redirect if any additional path is provided."""
    template = current_app.template_service.find(key)
    return redirect("/{}/{}".format(template.key, path))
