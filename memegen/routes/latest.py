from flask import Blueprint, render_template, current_app
from webargs import fields, flaskparser

from ._utils import route


blueprint = Blueprint('latest-page', __name__)


@blueprint.route("/latest")
@flaskparser.use_kwargs({'nsfw': fields.Bool(missing=False)})
def get(nsfw):
    return render_template(
        'latest.html',
        srcs=[route('image.get_latest', index=i, filtered=not nsfw)
              for i in range(30)],
        refresh=60,
        config=current_app.config,
    )
