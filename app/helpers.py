from typing import Dict, List, Tuple

from . import settings, utils
from .models import Template


def get_valid_templates(request) -> List[Dict]:
    templates = Template.objects.filter(valid=True)
    return [t.jsonify(request.app) for t in templates]


def get_sample_images(request) -> List[Tuple[str, str]]:
    return [
        (template.build_sample_url(request.app), template.build_self_url(request.app))
        for template in Template.objects.filter(valid=True)
    ]


def get_test_images(request) -> List[str]:
    return [
        request.app.url_for(
            "images.text", template_key=key, text_paths=utils.text.encode(lines)
        )
        for key, lines in settings.TEST_IMAGES
    ]
