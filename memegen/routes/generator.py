from flask import Blueprint, render_template
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._common import samples


blueprint = Blueprint('generator', __name__, url_prefix="/generator")


@blueprint.route("")
@set_renderers(HTMLRenderer)
def get():
    imgs = [img for img in samples()]
    # In the future, this could be provided via query param
    # as well as similar to top/bottom text
    selected_img = imgs[0]
    selected_img['selected'] = True
    return render_template('generator.html', imgs=imgs,
                           selected_img=selected_img)
