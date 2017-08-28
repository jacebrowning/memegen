from flask import Blueprint, render_template, current_app

from ._utils import samples


blueprint = Blueprint('examples-page', __name__)


@blueprint.route("/examples")
def get():
    sample_images = list(samples())
    return render_template(
        "examples.html",
        sample_images=sample_images,
        config=current_app.config,
    )
