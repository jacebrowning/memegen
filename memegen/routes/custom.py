from flask import Blueprint, render_template, current_app


blueprint = Blueprint('custom-page', __name__)


@blueprint.route("/custom")
def get():
    return render_template(
        'custom.html',
        fonts=sorted(current_app.font_service.all()),
        config=current_app.config,
    )
