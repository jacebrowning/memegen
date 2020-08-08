from pathlib import Path
from typing import Iterable

from . import settings, utils
from .models import Template


def get_sample_images(request) -> Iterable[str]:
    for template in Template.objects.filter(valid=True):
        yield template.build_sample_url(request.app)


def get_test_images(request) -> Iterable[str]:
    for key, lines in settings.TEST_IMAGES:
        yield request.app.url_for("images.text", key=key, slug=utils.text.encode(lines))


def save_image(
    key: str, slug: str, ext: str, *, directory: Path = settings.IMAGES_DIRECTORY,
) -> Path:
    template = Template.objects.get_or_none(key) or Template.objects.get("_error")
    lines = utils.text.decode(slug)
    path = utils.images.save(template, lines, ext=ext, directory=directory)
    return path
