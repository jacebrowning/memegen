from flask import Blueprint, render_template, current_app
from flask_cachecontrol import cache_for
from webargs import fields, flaskparser

from ._utils import route

REFRESH_SECONDS = 60

blueprint = Blueprint('latest-page', __name__)


@blueprint.route("/latest")
@cache_for(seconds=REFRESH_SECONDS - 1)
@flaskparser.use_kwargs({'nsfw': fields.Bool(missing=False)})
def get(nsfw):
    filtered = 'false' if nsfw else 'true'
    return render_template(
        'latest.html',
        srcs=[route('image.get_latest', index=i, filtered=filtered)
              for i in range(24)],
        refresh=REFRESH_SECONDS,
        config=current_app.config,
    )
