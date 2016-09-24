import random

from flask import Blueprint, Response, render_template, current_app

from ._settings import GITHUB_SLUG
from ._utils import get_tid, route


blueprint = Blueprint('index', __name__, url_prefix="/")


@blueprint.route("")
def get_index():
    template_images = list(_samples(blank=True))
    sample_images = list(_samples())
    return Response(render_template(
        "index.html",
        template_images=template_images,
        default_template=random.choice(template_images)['key'],
        sample_images=sample_images,
        github_slug=GITHUB_SLUG,
        ga_tid=get_tid(),
    ))


def _samples(blank=False):
    """Generate dictionaries of sample image data for template rendering."""
    for template in sorted(current_app.template_service.all()):
        path = "_" if blank else template.sample_path
        url = route('image.get', key=template.key, path=path)
        yield {
            'key': template.key,
            'name': template.name,
            'url': url,
        }
