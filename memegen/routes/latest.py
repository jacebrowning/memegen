from flask import Blueprint, render_template, current_app
from flask_api.decorators import set_renderers
from flask_api.renderers import HTMLRenderer

from ._utils import route


blueprint = Blueprint('latest-page', __name__)


@blueprint.route("/latest")
@set_renderers(HTMLRenderer)
def get():
    return render_template(
        'latest.html',
        srcs=[route('image.get_latest', index=i) for i in range(1, 18 + 1)],
        refresh=30,
        config=current_app.config,
    )
