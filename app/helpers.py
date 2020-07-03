from pathlib import Path
from typing import Optional

from . import images
from .models import Template


def save_image(key: str, lines: str = "_", *, path: Optional[Path] = None) -> Path:
    template = Template.objects.get_or_none(key) or Template.objects.get("_error")
    path = images.save(template, lines, path=path)
    return path
