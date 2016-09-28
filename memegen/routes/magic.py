from flask import Blueprint, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._utils import get_tid


blueprint = Blueprint('magic-page', __name__)


@blueprint.route("/magic")
@set_renderers(HTMLRenderer)
def get():
    return render_template(
        'magic.html',
        ga_tid=get_tid(),
    )
