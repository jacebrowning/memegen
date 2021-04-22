from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from sanic.log import logger

from .. import settings
from ..types import Dimensions, Offset, Point, Text

if TYPE_CHECKING:
    from ..models import Template

EXCEPTIONS = (OSError, SyntaxError, Image.DecompressionBombError)


def preview(
    template: Template,
    lines: list[str],
    *,
    style: str = settings.DEFAULT_STYLE,
) -> tuple[bytes, str]:
    path = template.build_path(lines, style, settings.PREVIEW_SIZE, "", "jpg")
    logger.info(f"Previewing meme for {path}")
    image = render_image(
        template,
        style,
        lines,
        settings.PREVIEW_SIZE,
        pad=False,
        is_preview=True,
    )
    stream = io.BytesIO()
    image.convert("RGB").save(stream, format="JPEG", quality=50)
    return stream.getvalue(), "image/jpeg"


def save(
    template: Template,
    lines: list[str],
    watermark: str = "",
    *,
    ext: str = settings.DEFAULT_EXT,
    style: str = settings.DEFAULT_STYLE,
    size: Dimensions = (0, 0),
    directory: Path = settings.IMAGES_DIRECTORY,
) -> Path:
    size = fit_image(*size)

    path = directory / template.build_path(lines, style, size, watermark, ext)
    if path.exists():
        if settings.DEPLOYED:
            logger.info(f"Loading meme from {path}")
            return path
        logger.info(f"Reloading meme at {path}")
    else:
        logger.info(f"Saving meme to {path}")
        path.parent.mkdir(parents=True, exist_ok=True)

    image = render_image(template, style, lines, size, watermark=watermark)
    image.convert("RGB").save(path, quality=95)

    return path


def load(path: Path) -> Image:
    image = Image.open(path).convert("RGBA")
    image = ImageOps.exif_transpose(image)
    return image


def embed(template: Template, foreground_path: Path, background_path: Path) -> Image:
    background = load(background_path)

    for overlay in template.overlay:
        foreground = load(foreground_path)

        size = overlay.get_size(background.size)
        foreground.thumbnail(size)

        box = overlay.get_box(background.size, foreground.size)
        background.paste(foreground, box, foreground.convert("RGBA"))

    background.convert("RGB").save(foreground_path)
    return foreground_path


def render_image(
    template: Template,
    style: str,
    lines: list[str],
    size: Dimensions,
    *,
    pad: Optional[bool] = None,
    is_preview: bool = False,
    watermark: str = "",
) -> Image:
    background = load(template.get_image(style))

    pad = all(size) if pad is None else pad
    image = resize_image(background, *size, pad)
    if size[0] and size[0] <= settings.PREVIEW_SIZE[0] and not settings.DEBUG:
        watermark = ""

    for (
        point,
        offset,
        text,
        max_text_size,
        text_fill,
        font,
        stroke_width,
        stroke_fill,
        angle,
    ) in get_image_elements(template, lines, watermark, image.size, is_preview):

        box = Image.new("RGBA", max_text_size)
        draw = ImageDraw.Draw(box)

        if settings.DEBUG:
            xy = (0, 0, max_text_size[0] - 1, max_text_size[1] - 1)
            draw.rectangle(xy, outline="lime")

        draw.text(
            (-offset[0], -offset[1]),
            text,
            text_fill,
            font,
            spacing=-offset[1] / 2,
            align="center",
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

        box = box.rotate(angle, resample=Image.BICUBIC, expand=True)
        image.paste(box, point, box)

    if settings.DEBUG:
        draw = ImageDraw.Draw(image)
        for overlay in template.overlay:
            xy = overlay.get_box(image.size)
            draw.rectangle(xy, outline="fuchsia")

    if pad:
        image = add_blurred_background(image, background, *size)

    if watermark:
        image = add_watermark(image, watermark)

    return image


def resize_image(image: Image, width: int, height: int, pad: bool) -> Image:
    ratio = image.width / image.height
    default_width, default_height = settings.DEFAULT_SIZE

    if pad:
        if width < height * ratio:
            size = width, int(width / ratio)
        else:
            size = int(height * ratio), height
    elif width:
        size = width, int(width / ratio)
    elif height:
        size = int(height * ratio), height
    elif ratio < 1.0:
        size = default_width, int(default_height / ratio)
    else:
        size = int(default_width * ratio), default_height

    image = image.resize(size, Image.LANCZOS)
    return image


def fit_image(width: float, height: float) -> tuple[int, int]:
    while width * height > settings.MAXIMUM_PIXELS:
        width *= 0.75
        height *= 0.75
    return int(width), int(height)


def add_blurred_background(
    foreground: Image, background: Image, width: int, height: int
) -> Image:
    base_width, base_height = foreground.size

    border_width = min(width, base_width + 2)
    border_height = min(height, base_height + 2)
    border_dimensions = border_width, border_height
    border = Image.new("RGB", border_dimensions)
    border.paste(
        foreground,
        ((border_width - base_width) // 2, (border_height - base_height) // 2),
    )

    padded = background.resize((width, height), Image.LANCZOS)
    darkened = padded.point(lambda p: int(p * 0.4))
    blurred = darkened.filter(ImageFilter.GaussianBlur(5))

    blurred_width, blurred_height = blurred.size
    offset = (
        (blurred_width - border_width) // 2,
        (blurred_height - border_height) // 2,
    )
    blurred.paste(border, offset)

    return blurred


def add_watermark(image: Image, text: str) -> Image:
    size = (image.size[0], settings.WATERMARK_HEIGHT)
    font = get_font(text, 0.0, size, 99, tiny=True)
    offset = get_text_offset(text, font, size)

    watermark = Text.get_watermark()
    stroke_width, stroke_fill = watermark.get_stroke(get_stroke_width(font))

    box = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(box)
    draw.text(
        (3, image.size[1] - size[1] - offset[1] - 1),
        text,
        watermark.color,
        font,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )

    return Image.alpha_composite(image, box)


def get_image_elements(
    template: Template,
    lines: list[str],
    watermark: str,
    image_size: Dimensions,
    is_preview: bool = False,
) -> Iterator[tuple[Point, Offset, str, Dimensions, str, ImageFont, int, str, float]]:

    for index, text in enumerate(template.text):
        yield get_image_element(lines, index, text, image_size, watermark)
    if is_preview:
        lines = ["PREVIEW"]
        index = 0
        text = Text.get_preview()
        yield get_image_element(lines, index, text, image_size, watermark)


def get_image_element(
    lines: list[str], index: int, text: Text, image_size: Dimensions, watermark: str
) -> tuple[Point, Offset, str, Dimensions, str, ImageFont, int, str, float]:
    point = text.get_anchor(image_size, watermark)

    max_text_size = text.get_size(image_size)
    max_font_size = int(image_size[1] / (2 if text.angle else 9))

    thin = False
    try:
        line = lines[index]
    except IndexError:
        line = ""
    else:
        line, thin = text.stylize(wrap(line, max_text_size, max_font_size), lines=lines)

    font = get_font(line, text.angle, max_text_size, max_font_size, thin=thin)
    offset = get_text_offset(line, font, max_text_size)

    stroke_width, stroke_fill = text.get_stroke(get_stroke_width(font))

    return (
        point,
        offset,
        line,
        max_text_size,
        text.color,
        font,
        stroke_width,
        stroke_fill,
        text.angle,
    )


def wrap(line: str, max_text_size: Dimensions, max_font_size: int) -> str:
    lines = split(line)

    single = get_font(line, 0, max_text_size, max_font_size)
    double = get_font(lines, 0, max_text_size, max_font_size)

    if single.size == double.size and double.size <= settings.MINIMUM_FONT_SIZE:
        return lines

    if single.size >= double.size:
        return line

    if get_text_size(lines, double)[0] >= max_text_size[0] * 0.60:
        return lines

    return line


def split(line: str) -> str:
    midpoint = len(line) // 2 - 1

    for offset in range(0, len(line) // 4):
        for index in [midpoint - offset, midpoint + offset]:
            if line[index] == " ":
                return line[:index] + "\n" + line[index:]

    return line


def get_font(
    text: str,
    angle: float,
    max_text_size: Dimensions,
    max_font_size: int,
    *,
    tiny: bool = False,
    thin: bool = False,
) -> ImageFont:
    max_text_width = max_text_size[0] - max_text_size[0] / 35
    max_text_height = max_text_size[1] - max_text_size[1] / 10

    for size in range(max(settings.MINIMUM_FONT_SIZE, max_font_size), 6, -1):

        if tiny:
            font = ImageFont.truetype(str(settings.FONT_TINY), size=size)
        elif angle or thin:
            font = ImageFont.truetype(str(settings.FONT_THIN), size=size)
        else:
            font = ImageFont.truetype(str(settings.FONT_THICK), size=size)

        text_width, text_height = get_text_size_minus_font_offset(text, font)
        if text_width <= max_text_width and text_height <= max_text_height:
            break

    return font


def get_text_size_minus_font_offset(text: str, font: ImageFont) -> Dimensions:
    text_width, text_height = get_text_size(text, font)
    offset = font.getoffset(text)
    return text_width - offset[0], text_height - offset[1]


def get_text_offset(text: str, font: ImageFont, max_text_size: Dimensions) -> Offset:
    text_size = get_text_size(text, font)
    stroke_width = get_stroke_width(font)

    x_offset, y_offset = font.getoffset(text)

    x_offset -= stroke_width
    y_offset -= stroke_width

    x_offset -= (max_text_size[0] - text_size[0]) / 2
    y_offset -= (max_text_size[1] - text_size[1] / (1.25 if "\n" in text else 1.5)) // 2

    return x_offset, y_offset


def get_text_size(text: str, font: ImageFont) -> Dimensions:
    image = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(image)
    text_size = draw.textsize(text, font)
    stroke_width = get_stroke_width(font)
    return text_size[0] + stroke_width, text_size[1] + stroke_width


def get_stroke_width(font: ImageFont) -> int:
    return min(3, max(1, font.size // 12))
