from collections import OrderedDict

from flask import Blueprint, current_app as app, url_for, redirect

from ..domain import Image


blueprint = Blueprint('links', __name__, url_prefix="/")


@blueprint.route("<key>/<top>/<bottom>")
def get(**kwargs):
    """Get links for generated images."""
    data = OrderedDict()
    data['visible'] = OrderedDict()
    data['hidden'] = OrderedDict()
    for kind in Image.KINDS:
        url = url_for('image.get', kind=kind.lower(), _external=True, **kwargs)
        data['visible'][kind] = url
        code = app.link_service.encode(**kwargs)
        url = url_for('image.get_encoded', kind=kind.lower(), _external=True, code=code)
        data['hidden'][kind] = url
    return data


@blueprint.route("<code>")
def get_encoded(code):
    key, top, bottom = app.link_service.decode(code)
    url = url_for('.get', key=key, top=top, bottom=bottom)
    return redirect(url)
