from pathlib import Path
from unittest.mock import Mock

import pytest

from ..models import Template
from ..views.helpers import preview_image


@pytest.mark.asyncio
async def test_preview_images(images: Path, template: Template):
    path = images / "preview.jpg"
    response = await preview_image(
        Mock(args={}), template.id, "", ["nominal image", "while typing"]
    )
    path.write_bytes(response.body)


@pytest.mark.asyncio
async def test_preview_images_top_layout(images: Path, template: Template):
    template = await template.clone({"layout": "top"}, lines=2, animated=False)
    path: Path = images / "preview-top.jpg"
    response = await preview_image(
        Mock(args={}), template.id, "", ["Nominal image", "while typing"]
    )
    path.write_bytes(response.body)


@pytest.mark.asyncio
async def test_preview_images_animated(images: Path, template: Template):
    path = images / "preview-animated.jpg"
    response = await preview_image(
        Mock(args={}), template.id, "animated", ["animated image", "while typing"]
    )
    path.write_bytes(response.body)
