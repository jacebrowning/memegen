from collections import OrderedDict

from flask import Blueprint, current_app as app, redirect
from webargs import fields, flaskparser

from ._common import route


blueprint = Blueprint('aliases', __name__)

FILTER = {
    'name': fields.Str(missing="")  # pylint: disable=no-member
}


@blueprint.route("/aliases/")
@flaskparser.use_kwargs(FILTER)
def get(name):
    """Get a list of all matching aliases."""
    if name:
        return redirect(route('.get_with_name', name=name))
    else:
        return []


@blueprint.route("/aliases/<name>")
def get_with_name(name):
    """Get a list of all matching aliases."""
    return _get_aliases(name)


def _get_aliases(name=""):
    items = OrderedDict()

    for alias in sorted(app.template_service.aliases(name)):
        template = app.template_service.find(alias)

        data = OrderedDict()
        data['styles'] = sorted(template.styles)
        data['template'] = \
            route('templates.create', key=template.key, _external=True)

        items[alias] = data

    return items
