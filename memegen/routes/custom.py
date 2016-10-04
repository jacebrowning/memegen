from flask import Blueprint, render_template, current_app
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._utils import get_tid


blueprint = Blueprint('custom-page', __name__)


@blueprint.route("/custom")
@set_renderers(HTMLRenderer)
def get():
    return render_template(
        'custom.html',
        fonts=current_app.font_service.all(),
        ga_tid=get_tid(),
    )
