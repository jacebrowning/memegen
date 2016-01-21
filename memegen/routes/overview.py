from flask import Blueprint, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._common import samples


blueprint = Blueprint('overview', __name__, url_prefix="/overview")


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    return render_template('overview.html', imgs=samples())
