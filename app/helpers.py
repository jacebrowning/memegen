from typing import Dict, List, Tuple
from urllib.parse import unquote

import aiohttp
from cachetools import cached
from sanic.log import logger
from sanic_cors import CORS
from sanic_openapi import swagger_blueprint

from . import api, errors, settings, utils
from .models import Template


def configure(app):
    app.config.API_HOST = app.config.SERVER_NAME = settings.SERVER_NAME
    app.config.API_BASEPATH = "/"
    app.config.API_SCHEMES = [settings.SCHEME]
    app.config.API_VERSION = "6.1"
    app.config.API_TITLE = "Memegen API"
    app.config.API_CONTACT_EMAIL = "support@maketested.com"
    app.config.API_LICENSE_NAME = "View license"
    app.config.API_LICENSE_URL = (
        "https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt"
    )
    app.config.API_SECURITY = [{"ApiKeyAuth": []}]
    app.config.API_SECURITY_DEFINITIONS = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
    }

    swagger_blueprint.url_prefix = "/docs"
    app.blueprint(swagger_blueprint)

    app.blueprint(api.images.blueprint)
    app.blueprint(api.templates.blueprint)
    app.blueprint(api.shortcuts.blueprint)

    CORS(app)
    app.error_handler = errors.BugsnagErrorHandler()


@cached({}, key=lambda _: settings.SERVER_NAME)
def get_valid_templates(request) -> List[Dict]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    return [t.jsonify(request.app) for t in templates]


@cached({}, key=lambda _: settings.SERVER_NAME)
def get_sample_images(request) -> List[Tuple[str, str]]:
    return [
        (template.build_sample_url(request.app), template.build_self_url(request.app))
        for template in Template.objects.filter(valid=True, _exclude="_custom")
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


async def track(request, lines):
    if settings.REMOTE_TRACKING_URL:  # pragma: no cover
        async with aiohttp.ClientSession() as session:
            params = dict(
                text=" ".join(lines),
                source="memegen.link",
                context=unquote(request.url),
            )
            response = await session.get(settings.REMOTE_TRACKING_URL, params=params)
            if response.status != 200:
                logger.error(f"Tracker response: {await response.json()}")
