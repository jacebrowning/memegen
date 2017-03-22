import random

from flask import Blueprint, render_template, current_app

from ._utils import route


blueprint = Blueprint('index-page', __name__)


@blueprint.route("/")
def get_index():
    template_images = list(_samples(blank=True))
    sample_images = list(_samples())
    return render_template(
        "index.html",
        template_images=template_images,
        default_template=random.choice(template_images)['key'],
        sample_images=sample_images,
        config=current_app.config,
    )


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
