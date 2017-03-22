from flask import Blueprint, render_template, current_app

from ._utils import route


blueprint = Blueprint('latest-page', __name__)


@blueprint.route("/latest")
def get():
    return render_template(
        'latest.html',
        srcs=[route('image.get_latest', index=i) for i in range(30)],
        refresh=60,
        config=current_app.config,
    )
