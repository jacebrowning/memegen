from pathlib import Path
from typing import Iterator, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from .. import settings
from ..models import Template
from ..types import Dimensions, Point
from .text import encode


def save(
    template: Template,
    lines: List[str],
    *,
    ext: str = settings.DEFAULT_EXT,
    size: Dimensions = settings.DEFAULT_SIZE,
    directory: Path = settings.IMAGES_DIRECTORY,
) -> Path:
    slug = encode(lines)
    # TODO: is this the best filename?
    path = directory / template.key / f"{slug}.{ext}"
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

    image = _render_image(template, lines, size)
    image.save(path, quality=95)

    return path


def _render_image(template: Template, lines: List[str], size: Dimensions) -> Image:
    image = Image.open(template.background_image_path)
    image = image.convert("RGB")

    image.thumbnail(size, Image.LANCZOS)

    draw = ImageDraw.Draw(image)

    for (
        point,
        text,
        max_text_size,
        text_fill,
        font_size,
        stroke_width,
        stroke_fill,
    ) in _get_elements(template, lines, image.size):

        if settings.DEBUG:
            box = (point, (point[0] + max_text_size[0], point[1] + max_text_size[1]))
            draw.rectangle(box, outline="lime")

        font = ImageFont.truetype(str(settings.FONT), size=font_size)
        draw.text(
            point,
            text,
            text_fill,
            font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

    return image


def _get_elements(
    template: Template, lines: List[str], image_size: Dimensions
) -> Iterator[Tuple[Point, str, Dimensions, str, int, int, str]]:
    for index, text in enumerate(template.text):
        point = text.get_anchor(image_size)  # TODO: adjust for font.getoffset(text)

        try:
            line = lines[index]
        except IndexError:
            line = ""

        max_text_size = text.get_size(image_size)
        font = _get_font(line, max_text_size)

        stroke_width = min(3, max(1, font.size // 12))
        stroke_fill = "black" if text.color == "white" else "white"

        yield point, line, max_text_size, text.color, font.size, stroke_width, stroke_fill


def _get_font(text: str, max_text_size: Dimensions) -> ImageFont:
    max_text_width, max_text_height = max_text_size

    for size in range(72, 5, -1):
        font = ImageFont.truetype(str(settings.FONT), size=size)
        text_width, text_height = font.getsize(text)
        if text_width <= max_text_width and text_height <= max_text_height:
            break

    return font
