from flask import Blueprint, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer
from ._common import samples, get_tid

blueprint = Blueprint('future', __name__, url_prefix="/future")


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    imgs = [img for img in samples()]

    [print(img) for img in imgs]

    return render_template(
        'future.html',
        imgs=imgs
    )
