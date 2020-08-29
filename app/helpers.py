from typing import Dict, List, Tuple

from sanic_openapi import swagger_blueprint

from . import api, settings, utils
from .models import Template


def configure(app):
    app.config.SERVER_NAME = settings.SERVER_NAME
    app.config.API_SCHEMES = settings.API_SCHEMES
    app.config.API_VERSION = "6.0a1"
    app.config.API_TITLE = "Memegen API"
    app.config.API_LICENSE_NAME = "MIT License"
    app.config.API_LICENSE_URL = (
        "https://github.com/jacebrowning/memegen-api/blob/main/LICENSE.txt"
    )

    app.blueprint(api.images.blueprint)
    app.blueprint(api.templates.blueprint)
    app.blueprint(api.shortcuts.blueprint)

    swagger_blueprint.url_prefix = "/docs"
    app.blueprint(swagger_blueprint)


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
            f"images.text_{settings.DEFAULT_EXT}",
            template_key=key,
            text_paths=utils.text.encode(lines),
        )
        for key, lines in settings.TEST_IMAGES
    ]
