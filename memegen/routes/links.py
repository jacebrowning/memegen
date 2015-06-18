from collections import OrderedDict

from flask import Blueprint, current_app as app, url_for, redirect

from ..domain import Text


blueprint = Blueprint('links', __name__, url_prefix="/")


@blueprint.route("<key>/<path:path>")
def get(**kwargs):
    """Get links for generated images."""
    text = Text(kwargs['path'])
    if kwargs['path'] != text.path:
        kwargs['path'] = text.path
        return redirect(url_for(".get", **kwargs))

    data = OrderedDict()
    data['visible'] = url_for('image.get', _external=True, **kwargs)
    code = app.link_service.encode(**kwargs)
    data['hidden'] = url_for('image.get_encoded', _external=True, code=code)
    return data


@blueprint.route("<code>")
def get_encoded(code):
    key, path = app.link_service.decode(code)
    url = url_for('.get', key=key, path=path)
    return redirect(url)
