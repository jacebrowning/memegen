from flask import Blueprint, render_template, current_app, make_response


blueprint = Blueprint('custom-page', __name__)


@blueprint.route("/custom")
def get():
    html = render_template(
        'custom.html',
        fonts=sorted(current_app.font_service.all()),
        config=current_app.config,
    )
    response = make_response(html)
    response.headers['Cache-Control'] = f'max-age={60*60*24*7}'
    return response
