from collections import OrderedDict

from flask import Blueprint, current_app as app, url_for

from ..domain import Image


blueprint = Blueprint('link', __name__, url_prefix="/")


@blueprint.route("<key>/<top>/<bottom>")
def get(**kwargs):
    data = OrderedDict()
    data['visible'] = OrderedDict()
    data['hidden'] = OrderedDict()
    for kind in Image.KINDS:
        url = url_for('image.get_visible', kind=kind, _external=True, **kwargs)
        data['visible'][kind] = url
        code = app.link_service.encode(**kwargs)
        url = url_for('image.get_hidden', kind=kind, _external=True, code=code)
        data['hidden'][kind] = url
    return data
