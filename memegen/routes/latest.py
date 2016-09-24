from flask import Blueprint, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._utils import route, get_tid


blueprint = Blueprint('latest', __name__, url_prefix="/latest")


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    return render_template(
        'latest.html',
        srcs=[route('image.get_latest', index=i + 1) for i in range(9)],
        refresh=10,
        ga_tid=get_tid(),
    )
