from flask import Blueprint, render_template, current_app, make_response
from webargs import fields, flaskparser

from ._utils import route

REFRESH_SECONDS = 60

blueprint = Blueprint('latest-page', __name__)


@blueprint.route("/latest")
@flaskparser.use_kwargs({'nsfw': fields.Bool(missing=False)})
def get(nsfw):
    filtered = 'false' if nsfw else 'true'
    html = render_template(
        'latest.html',
        srcs=[route('image.get_latest', index=i, filtered=filtered)
              for i in range(24)],
        refresh=REFRESH_SECONDS,
        config=current_app.config,
    )
    response = make_response(html)
    response.headers['Cache-Control'] = f'max-age={REFRESH_SECONDS-1}'
    return response
