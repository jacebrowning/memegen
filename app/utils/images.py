from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from .. import settings
from ..types import Dimensions, Offset, Point
from .text import encode

if TYPE_CHECKING:
    from ..models import Template


def save(
    template: Template,
    lines: List[str],
    ext: str = settings.DEFAULT_EXT,
    *,
    size: Dimensions = settings.DEFAULT_SIZE,
    directory: Path = settings.IMAGES_DIRECTORY,
) -> Path:
    slug = encode(lines)
    # TODO: is this the best filename?
    path = directory / template.key / f"{slug}.{ext}"
    path.parent.mkdir(parents=True, exist_ok=True)

    image = _render_image(template, lines, size)
    image.save(path, quality=95)

    return path


def _render_image(template: Template, lines: List[str], size: Dimensions) -> Image:
    image = Image.open(template.image)
    image = image.convert("RGB")

    image.thumbnail(size, Image.LANCZOS)

    draw = ImageDraw.Draw(image)

    for (
        point,
        offset,
        text,
        max_text_size,
        text_fill,
        font_size,
        stroke_width,
        stroke_fill,
    ) in _get_elements(template, lines, image.size):

        if settings.DEBUG:
            box = (
                point,
                (point[0] + max_text_size[0], point[1] + max_text_size[1]),
            )
            draw.rectangle(box, outline="lime")

        font = ImageFont.truetype(str(settings.FONT), size=font_size)
        draw.text(
            (point[0] - offset[0], point[1] - offset[1]),
            text,
            text_fill,
            font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

    return image


def _get_elements(
    template: Template, lines: List[str], image_size: Dimensions
) -> Iterator[Tuple[Point, Offset, str, Dimensions, str, int, int, str]]:
    for index, text in enumerate(template.text):
        point = text.get_anchor(image_size)

        try:
            line = lines[index]
        except IndexError:
            line = ""
        else:
            line = text.stylize(line)

        max_text_size = text.get_size(image_size)

        font = _get_font(line, max_text_size)
        offset = _get_text_offset(line, font, max_text_size)

        stroke_width = min(3, max(1, font.size // 12))
        stroke_fill = "black" if text.color == "white" else "white"

        yield point, offset, line, max_text_size, text.color, font.size, stroke_width, stroke_fill


def _get_font(text: str, max_text_size: Dimensions) -> ImageFont:
    max_text_width, max_text_height = max_text_size

    for size in range(72, 5, -1):
        font = ImageFont.truetype(str(settings.FONT), size=size)
        text_width, text_height = _get_text_size_minus_offset(text, font)
        if text_width <= max_text_width and text_height <= max_text_height:
            break

    return font


def _get_text_size_minus_offset(text: str, font: ImageFont) -> Dimensions:
    text_width, text_height = font.getsize(text)
    offset = font.getoffset(text)
    return text_width - offset[0], text_height - offset[1]


def _get_text_offset(text: str, font: ImageFont, max_text_size: Dimensions) -> Offset:
    text_size = font.getsize(text)
    x_offset, y_offset = font.getoffset(text)

    x_offset -= (max_text_size[0] - text_size[0]) // 2
    y_offset -= (max_text_size[1] - (text_size[1] / 1.5)) // 2

    return x_offset, y_offset
