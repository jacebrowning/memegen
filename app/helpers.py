from sanic import Request

from . import settings, utils
from .models import Template


def get_valid_templates(
    request: Request, query: str = "", animated: bool | None = None
) -> list[dict]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)
    if animated is True:
        templates = [t for t in templates if "animated" in t.styles]
    elif animated is False:
        templates = [t for t in templates if "animated" not in t.styles]
    return [template.jsonify(request) for template in templates]


def get_example_images(
    request: Request, query: str = "", animated: bool | None = None
) -> list[tuple[str, str]]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)

    images = []
    for template in templates:

        if animated is True and "animated" not in template.styles:
            continue

        if "animated" in template.styles and animated is not False:
            extension = "gif"
        else:
            extension = settings.DEFAULT_EXTENSION

        example = template.build_example_url(request, extension=extension)
        self = template.build_self_url(request)
        images.append((example, self))

    return images


def get_test_images(request: Request) -> list[str]:
    return [
        request.app.url_for(
            "Memes.text",
            template_id=id,
            text_paths=utils.text.encode(lines) + "." + extension,
        )
        for id, lines, extension in settings.TEST_IMAGES
    ]
