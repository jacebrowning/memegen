from sanic import Request

from . import settings, utils
from .models import Template


def get_valid_templates(
    request: Request, query: str = "", animated: bool | None = None
) -> list[dict]:
    templates: list[Template] = Template.objects.filter(valid=True, _exclude="_custom")
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
    request: Request, query: str = "", *, animated: bool | None = None
) -> list[tuple[str, str]]:
    templates = Template.objects.filter(valid=True, _exclude="_custom")
    if query:
        templates = [t for t in templates if t.matches(query)]
    else:
        templates = sorted(templates)

    if animated is None:
        animated = utils.urls.flag(request, "animated")
        exact = True
    else:
        exact = False

    images = []
    for template in templates:

        if exact and animated is True and "animated" not in template.styles:
            continue
        if exact and animated is False and "animated" in template.styles:
            continue

        if animated is True:
            extension = settings.DEFAULT_ANIMATED_EXTENSION
        elif "animated" in template.styles and animated is not False:
            extension = settings.DEFAULT_ANIMATED_EXTENSION
        else:
            extension = settings.DEFAULT_STATIC_EXTENSION

        example = template.build_example_url(request, extension=extension)
        self = template.build_self_url(request)
        images.append((example, self))

    return images


def get_test_images(request: Request) -> list[str]:
    animated = utils.urls.flag(request, "animated")
    if animated:
        images = [
            image
            for image in settings.TEST_IMAGES
            if image[2] in settings.ANIMATED_EXTENSIONS
        ]
    else:
        images = settings.TEST_IMAGES

    return [
        request.app.url_for(
            "Images.detail_text",
            template_id=id,
            text_filepath=utils.text.encode(lines) + "." + extension,
        )
        for id, lines, extension in images
    ]
