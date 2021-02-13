from sanic_cors import CORS
from sanic_openapi import swagger_blueprint

from . import api, errors, settings, utils
from .models import Template


def configure(app):
    app.config.API_HOST = app.config.SERVER_NAME = settings.SERVER_NAME
    app.config.API_BASEPATH = "/"
    app.config.API_SCHEMES = [settings.SCHEME]
    app.config.API_VERSION = "8.1"
    app.config.API_TITLE = "Memegen.link"
    app.config.API_CONTACT_EMAIL = "support@maketested.com"
    app.config.API_LICENSE_NAME = "View the license"
    app.config.API_LICENSE_URL = (
        "https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt"
    )
    app.config.API_SECURITY = [{"ApiKeyAuth": []}]
    app.config.API_SECURITY_DEFINITIONS = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
    }

    swagger_blueprint.url_prefix = "/docs"
    app.blueprint(swagger_blueprint)

    app.blueprint(api.clients.blueprint)
    app.blueprint(api.memes.blueprint)
    app.blueprint(api.templates.blueprint)
    app.blueprint(api.shortcuts.blueprint)  # registered last to avoid collisions

    CORS(app)
    app.error_handler = errors.BugsnagErrorHandler()


def get_valid_templates(request) -> list[dict]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    return [template.jsonify(request.app) for template in sorted(templates)]


def get_example_images(request) -> list[tuple[str, str]]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    return [
        (
            template.build_example_url(request.app, "Memes.text_jpg"),
            template.build_self_url(request.app),
        )
        for template in sorted(templates)
    ]


def get_test_images(request) -> list[str]:
    return [
        request.app.url_for(
            f"Memes.text_{settings.DEFAULT_EXT}",
            template_id=id,
            text_paths=utils.text.encode(lines),
        )
        for id, lines in settings.TEST_IMAGES
    ]
