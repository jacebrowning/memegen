from collections import OrderedDict

from flask import Blueprint, current_app as app, redirect

from ..domain import Text

from ._common import url_for


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
    data['direct'] = OrderedDict()
    visible_url = url_for('image.get', key=key, path=path, _external=True)
    data['direct']['visible'] = visible_url
    code = app.link_service.encode(key, path)
    masked_url = url_for('image.get_encoded', code=code, _external=True)
    data['direct']['masked'] = masked_url
    data['markdown'] = OrderedDict()
    data['markdown']['visible'] = "![{k}]({u})".format(k=key, u=visible_url)
    data['markdown']['masked'] = "![{k}]({u})".format(k=key, u=masked_url)
    return data


@blueprint.route("_<code>")
def get_encoded(code):
    key, path = app.link_service.decode(code)
    return redirect(url_for('.get', key=key, path=path))
