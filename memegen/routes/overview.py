from flask import Blueprint, current_app as app, url_for, render_template
# http://stackoverflow.com/questions/16061514/pylint-pylint-unable-to-import-flask-ext-wtf
from flask.ext.api.decorators import set_renderers  # pylint: disable=E0611,F0401
from flask.ext.api.renderers import HTMLRenderer  # pylint: disable=E0611,F0401


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
