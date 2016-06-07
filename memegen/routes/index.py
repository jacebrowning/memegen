import random

from flask import Blueprint, Response, render_template

from ._common import GITHUB_SLUG, get_tid, samples


blueprint = Blueprint('index', __name__, url_prefix="/")


@blueprint.route("")
def get_index():
    template_images = list(samples(blank=True))
    sample_images = list(samples())
    return Response(render_template(
        "index.html",
        template_images=template_images,
        default_template=random.choice(template_images)['key'],
        sample_images=sample_images,
        github_slug=GITHUB_SLUG,
        ga_tid=get_tid(),
    ))
