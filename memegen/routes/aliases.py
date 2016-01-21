from collections import OrderedDict

from flask import Blueprint, current_app as app
from webargs import fields, flaskparser

from ._common import route


blueprint = Blueprint('aliases', __name__, url_prefix="/aliases/")

FILTER = {
    'name': fields.Str(missing="")  # pylint: disable=no-member
}


@blueprint.route("")
@flaskparser.use_kwargs(FILTER)
def get(name):
    """Get a list of all matching aliases."""
    items = OrderedDict()

    for alias in sorted(app.template_service.aliases(name)):
        template = app.template_service.find(alias)

        data = OrderedDict()
        data['styles'] = sorted(template.styles)
        data['template'] = \
            route('templates.create', key=template.key, _external=True)

        items[alias] = data

    return items
