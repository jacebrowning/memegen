from pathlib import Path

from . import settings, utils
from .models import Template


def save_image(
    key: str, slug: str, ext: str, *, directory: Path = settings.IMAGES_DIRECTORY,
) -> Path:
    template = Template.objects.get_or_none(key) or Template.objects.get("_error")
    lines = utils.text.decode(slug)
    path = utils.images.save(template, lines, ext=ext, directory=directory)
    return path
