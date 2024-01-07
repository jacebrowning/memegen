from pathlib import Path
from unittest.mock import Mock

import pytest

from ..models import Template
from ..views.helpers import preview_image


@pytest.mark.asyncio
async def test_preview_images(images: Path, template: Template):
    request = Mock(args={})
    lines = ["nominal image", "while typing"]
    path = images / "preview.jpg"
    response = await preview_image(request, template.id, "", lines)
    path.write_bytes(response.body)


@pytest.mark.asyncio
async def test_preview_images_top_layout(images: Path, template: Template):
    request = Mock(args={"layout": "top"})
    lines = ["Nominal image", "while typing"]
    path: Path = images / "preview-top.jpg"
    response = await preview_image(request, template.id, "", lines)
    path.write_bytes(response.body)


@pytest.mark.asyncio
async def test_preview_images_animated(images: Path, template: Template):
    request = Mock(args={})
    lines = ["animated image", "while typing"]
    path = images / "preview-animated.jpg"
    response = await preview_image(request, template.id, "animated", lines)
    path.write_bytes(response.body)
