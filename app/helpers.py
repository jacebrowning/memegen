from sanic import Request

from . import settings, utils
from .models import Template


def get_valid_templates(request: Request, query: str = "") -> list[dict]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)
    return [template.jsonify(request) for template in templates]


def get_example_images(request: Request, query: str = "") -> list[tuple[str, str]]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)
    return [
        (
            template.build_example_url(request),
            template.build_self_url(request),
        )
        for template in templates
    ]


def get_test_images(request: Request) -> list[str]:
    return [
        request.app.url_for(
            "Memes.text",
            template_id=id,
            text_paths=utils.text.encode(lines) + "." + extension,
        )
        for id, lines, extension in settings.TEST_IMAGES
    ]
