from flask import Blueprint, render_template, current_app


blueprint = Blueprint('magic-page', __name__)


@blueprint.route("/magic")
def get():
    return render_template(
        'magic.html',
        config=current_app.config
    )
