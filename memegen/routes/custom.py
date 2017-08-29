from flask import Blueprint, render_template, current_app
from flask_cachecontrol import cache_for


blueprint = Blueprint('custom-page', __name__)


@blueprint.route("/custom")
@cache_for(days=7)
def get():
    return render_template(
        'custom.html',
        fonts=sorted(current_app.font_service.all()),
        config=current_app.config,
    )
