from . import settings, utils
from .models import Template


def get_valid_templates(request, query: str = "") -> list[dict]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)
    return [template.jsonify(request.app) for template in templates]


def get_example_images(request, query: str = "") -> list[tuple[str, str]]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)
    return [
        (
            template.build_example_url(request.app),
            template.build_self_url(request.app),
        )
        for template in templates
    ]


def get_test_images(request) -> list[str]:
    return [
        request.app.url_for(
            f"Memes.text_{settings.DEFAULT_EXTENSION}",
            template_id=id,
            text_paths=utils.text.encode(lines) + "." + settings.DEFAULT_EXTENSION,
        )
        for id, lines in settings.TEST_IMAGES
    ]
