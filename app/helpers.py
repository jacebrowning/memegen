from typing import Dict, List

from . import settings, utils
from .models import Template


def get_valid_templates(request) -> List[Dict]:
    templates = Template.objects.filter(valid=True)
    return [t.jsonify(request.app) for t in templates]


def get_sample_images(request) -> List[str]:
    return [
        template.build_sample_url(request.app)
        for template in Template.objects.filter(valid=True)
    ]


def get_test_images(request) -> List[str]:
    return [
        request.app.url_for("images.text", key=key, slug=utils.text.encode(lines))
        for key, lines in settings.TEST_IMAGES
    ]
