import random

from flask import Blueprint, render_template, current_app

from ._utils import samples


blueprint = Blueprint('index-page', __name__)


@blueprint.route("/")
def get():
    template_images = list(samples(blank=True))
    return render_template(
        "index.html",
        template_images=template_images,
        default_template=random.choice(template_images)['key'],
        config=current_app.config,
    )
