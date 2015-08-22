from flask import Blueprint, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._common import url_for


blueprint = Blueprint('latest', __name__, url_prefix="/latest")


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    return render_template('latest.html', src=url_for("image.get_latest"))
