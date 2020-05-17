from pathlib import Path
from typing import Iterator, Optional, Tuple

from PIL import Image, ImageDraw

from .models import Template

Point = Tuple[int, int]


def save(template: Template, lines: str, *, path: Optional[Path] = None) -> Path:
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

    image = render(template, lines)
    image.save(path)

    return path


def render(template: Template, lines: str) -> Image:
    image = Image.open(template.background_image_path)
    draw = ImageDraw.Draw(image, "RGBA")

    for point, text in build(template, lines):
        draw.text(point, text)

    return image


def build(template: Template, lines: str) -> Iterator[Tuple[Point, str]]:
    for index, text in enumerate(lines.split("/")):
        yield (10, 10 + index * 20), text
