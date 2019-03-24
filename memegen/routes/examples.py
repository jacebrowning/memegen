from flask import Blueprint, render_template, current_app, make_response

from ._utils import samples


blueprint = Blueprint('examples-page', __name__)


@blueprint.route("/examples")
def get():
    sample_images = list(samples())
    html = render_template(
        "examples.html",
        sample_images=sample_images,
        config=current_app.config,
    )
    response = make_response(html)
    response.headers['Cache-Control'] = f'max-age={60*60*24*7}'
    return response
