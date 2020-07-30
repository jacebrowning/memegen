from pathlib import Path
from typing import Iterator, Optional, Tuple

from PIL import Image, ImageDraw

from .models import Template
from .types import Dimensions, Point


def save(
    template: Template,
    lines: str,
    size: Dimensions = (500, 500),
    *,
    path: Optional[Path] = None,
) -> Path:
    path = path or Path(f"images/{template.key}/{lines}.jpg")
    path.parent.mkdir(parents=True, exist_ok=True)

    # TODO: handle external images
    # background_image_path = self._get_background_image_path()
    # background_image_url = f"{settings.IMAGES_URL}/{background_image_path}"
    # log.debug(f"Fetching background image: {background_image_url}")

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(background_image_url) as response:
    #         if response.status == 200:
    #             f = await aiofiles.open(image_path, mode="wb")
    #             await f.write(await response.read())
    #             await f.close()
    #             images.render_legacy(image_path, lines)

    image = render(template, lines, size)
    image.save(path, format=image.format)

    return path


def render(template: Template, lines: str, size: Dimensions) -> Image:
    image = Image.open(template.background_image_path)
    image = image.convert("RGB")
    image = image.resize(size)  # TODO: preseve aspect ratio

    draw = ImageDraw.Draw(image)
    for point, text in build(template, lines, size):
        draw.text(point, text)

    return image


def build(
    template: Template, lines: str, size: Dimensions
) -> Iterator[Tuple[Point, str]]:
    parts = lines.split("/") + ["_", "_", "_"]
    for index, text in enumerate(template.text):
        yield text.get_anchor(size), parts[index]
