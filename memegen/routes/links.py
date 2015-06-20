from collections import OrderedDict

from flask import Blueprint, current_app as app, url_for, redirect

from ..domain import Text


blueprint = Blueprint('links', __name__, url_prefix="/")


@blueprint.route("<key>")
def get_without_text(key):
    template = app.template_service.find(key)
    if template.key != key:
        return redirect(url_for(".get_without_text", key=template.key))

    text = Text(template.default or '_')
    return redirect(url_for(".get", key=key, path=text.path))


@blueprint.route("<key>/<path:path>", endpoint='get')
def get_with_text(key, path):
    """Get links for generated images."""
    template = app.template_service.find(key)
    if template.key != key:
        return redirect(url_for(".get", key=template.key, path=path))

    text = Text(path)
    if text.path != path:
        return redirect(url_for(".get", key=key, path=text.path))

    data = OrderedDict()
    data['visible'] = url_for('image.get', key=key, path=path, _external=True)
    code = app.link_service.encode(key, path)
    data['hidden'] = url_for('image.get_encoded', _external=True, code=code)
    return data


@blueprint.route("_<code>")
def get_encoded(code):
    key, path = app.link_service.decode(code)
    return redirect(url_for('.get', key=key, path=path))
