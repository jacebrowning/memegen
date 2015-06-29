from flask import Blueprint, current_app as app, url_for, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer


blueprint = Blueprint('overview', __name__, url_prefix="/overview")


def _urls_generator():
    for template in sorted(app.template_service.all()):
        url = url_for("image.get", key=template.key, path="hello-world",
                      _external=True)
        yield url


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    return render_template('overview.html', urls=_urls_generator())
