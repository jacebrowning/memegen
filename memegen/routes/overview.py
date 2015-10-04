from flask import Blueprint, current_app as app, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._common import url_for


blueprint = Blueprint('overview', __name__, url_prefix="/overview")


def _gen():
    for template in sorted(app.template_service.all()):
        path = template.sample_path
        url = url_for("image.get", key=template.key, path=path, _external=True)
        link = url_for("links.get", key=template.key, path=path)
        yield {
            'url': url,
            'link': link
        }


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    return render_template('overview.html', imgs=_gen())
