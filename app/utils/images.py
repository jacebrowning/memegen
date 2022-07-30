from __future__ import annotations

import io
from pathlib import Path
from typing import Iterator

from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont,
    ImageOps,
    ImageSequence,
    UnidentifiedImageError,
)
from sanic.log import logger

from .. import settings
from ..models import Font, Template, Text
from ..types import Dimensions, FontType, ImageType, Offset, Point

EXCEPTIONS = (
    OSError,
    SyntaxError,
    Image.DecompressionBombError,
    UnidentifiedImageError,
)


def preview(
    template: Template,
    lines: list[str],
    *,
    style: str = "default",
    watermark: str = "",
) -> tuple[bytes, str]:
    path = template.build_path(lines, "", style, settings.PREVIEW_SIZE, "", "jpg")
    logger.info(f"Previewing meme for {path}")
    image = render_image(
        template,
        style,
        lines,
        settings.PREVIEW_SIZE,
        pad=False,
        is_preview=True,
        watermark=watermark,
    )
    stream = io.BytesIO()
    image.convert("RGB").save(stream, format="JPEG", quality=50)
    return stream.getvalue(), "image/jpeg"


def save(
    template: Template,
    lines: list[str],
    watermark: str = "",
    *,
    font_name: str = "",
    extension: str = settings.DEFAULT_EXTENSION,
    style: str = "default",
    size: Dimensions = (0, 0),
    maximum_frames: int = 0,
    directory: Path = settings.IMAGES_DIRECTORY,
) -> Path:
    size = fit_image(*size)

    path = directory / template.build_path(
        lines, font_name, style, size, watermark, extension, maximum_frames
    )
    if path.exists():
        if settings.DEPLOYED:
            logger.info(f"Loading meme from {path}")
            return path
        logger.info(f"Rebuilding meme at {path}")
    else:
        logger.info(f"Saving meme to {path}")
        path.parent.mkdir(parents=True, exist_ok=True)

    if extension == "gif":
        frames, duration = render_animation(
            template, style, lines, size, font_name, maximum_frames, watermark=watermark
        )

        count = len(frames)
        if "apng" in settings.ALLOWED_EXTENSIONS:
            if (count <= settings.MINIMUM_FRAMES) or (count > settings.MAXIMUM_FRAMES):
                extension = "png"

        if extension == "png":
            logger.info(f"Saving {count} frame(s) as APNG at {duration} duration")
        else:
            logger.info(f"Saving {count} frame(s) as GIF at {duration} duration")

        frames[0].save(
            path,
            format=extension,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
        )
    else:
        image = render_image(
            template, style, lines, size, font_name, watermark=watermark
        )
        image.convert("RGB").save(path, quality=95)

    return path


def load(path: Path) -> ImageType:
    image = Image.open(path).convert("RGBA")
    image = ImageOps.exif_transpose(image)
    return image


def embed(template: Template, index: int, foreground_path: Path, background_path: Path):
    try:
        overlay = template.overlay[index]
    except IndexError:
        count = len(template.overlay)
        logger.error(f"Template {template.id!r} only supports {count} overlay(s)")
        overlay = template.overlay[count - 1]

    background = load(background_path)
    foreground = load(foreground_path)

    size = overlay.get_size(background.size)
    foreground = foreground.resize(size, Image.LANCZOS)
    foreground = foreground.rotate(overlay.angle, expand=True)

    x1, y1, _x2, _y2 = overlay.get_box(background.size, foreground.size)
    background.paste(foreground, (x1, y1), mask=foreground.convert("RGBA"))

    background.convert("RGB").save(background_path)


def merge(template: Template, index: int, foreground_path: Path, background_path: Path):
    try:
        overlay = template.overlay[index]
    except IndexError:
        count = len(template.overlay)
        logger.error(f"Template {template.id!r} only supports {count} overlay(s)")
        overlay = template.overlay[count - 1]

    background = Image.open(background_path)
    foreground = load(foreground_path)

    frames = []
    for frame in ImageSequence.Iterator(background):
        stream = io.BytesIO()
        frame.save(stream, format="GIF")
        background = Image.open(stream).convert("RGBA")

        size = overlay.get_size(background.size)
        foreground.thumbnail(size)
        foreground = foreground.rotate(overlay.angle, expand=True)

        x1, y1, _x2, _y2 = overlay.get_box(background.size, foreground.size)
        background.paste(foreground, (x1, y1), mask=foreground.convert("RGBA"))

        frames.append(background)

    logger.debug(f"Merging {len(frames)} frame(s) for custom GIF background")
    frames[0].save(background_path, save_all=True, append_images=frames[1:])


def render_image(
    template: Template,
    style: str,
    lines: list[str],
    size: Dimensions,
    font_name: str = "",
    *,
    pad: bool | None = None,
    is_preview: bool = False,
    watermark: str = "",
) -> ImageType:
    background = load(template.get_image(style))

    pad = all(size) if pad is None else pad
    image = resize_image(background, *size, pad, expand=True)
    if any(
        (
            size[0] and size[0] <= settings.PREVIEW_SIZE[0],
            size[1] and size[1] <= settings.PREVIEW_SIZE[1],
        )
    ) and not (is_preview or settings.DEBUG):
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
    ) in get_image_elements(
        template, lines, font_name, watermark, image.size, is_preview
    ):

        box = Image.new("RGBA", max_text_size)
        draw = ImageDraw.Draw(box)

        if settings.DEBUG:
            xy = (0, 0, max_text_size[0] - 1, max_text_size[1] - 1)
            outline = "orange" if text == settings.PREVIEW_TEXT else "lime"
            draw.rectangle(xy, outline=outline)

        rows = text.count("\n") + 1
        draw.text(
            (-offset[0], -offset[1]),
            text,
            text_fill,
            font,
            spacing=-offset[1] / (rows * 2),
            # TODO: Match to text align
            align="center",
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )

        box = box.rotate(angle, resample=Image.BICUBIC, expand=True)
        image.paste(box, point, box)

    if settings.DEBUG:
        for overlay in template.overlay:
            box = Image.new("RGBA", overlay.get_size(image.size))
            draw = ImageDraw.Draw(box)
            draw.rectangle((0, 0, box.width - 1, box.height - 1), outline="fuchsia")

            # This offset math is inexact, but works well enough to see
            # approximately where rotated overlay images will be placed.
            # TODO: Implement a proper solution using trigonometry
            angle = abs(overlay.angle)
            if angle > 45:
                angle = 90 - angle
            offset = (
                int(angle + (22.5 - angle) / 22.5 - 1),
                int(angle + (22.5 - angle) / 22.5 - 1),
            )
            x1, y1, _x2, _y2 = overlay.get_box(image.size)
            point = (x1 - offset[0], y1 - offset[1])

            box = box.rotate(overlay.angle, expand=True)
            image.paste(box, point, mask=box)

    if pad:
        image = add_blurred_background(image, background, *size)

    if watermark:
        image = add_watermark(image, watermark, is_preview)

    return image


def render_animation(
    template: Template,
    style: str,
    lines: list[str],
    size: Dimensions,
    font_name: str = "",
    maximum_frames: int = 0,
    *,
    pad: bool | None = None,
    is_preview: bool = False,
    watermark: str = "",
) -> tuple[list[ImageType], int]:
    frames = []

    pad = all(size) if pad is None else pad
    source = Image.open(template.get_image(style, animated=True))
    duration = source.info.get("duration", 100)
    total = getattr(source, "n_frames", 1)
    if total > 1:
        sources = ImageSequence.Iterator(source)
    elif template.animated_text:
        sources = [source] * settings.MAXIMUM_FRAMES  # type: ignore
        duration = 250
        total = settings.MAXIMUM_FRAMES
    elif sum(1 for line in lines if line.strip()) == 2:
        template.animate()
        sources = [source] * settings.MINIMUM_FRAMES  # type: ignore
        duration = 1200
        total = settings.MINIMUM_FRAMES
    else:
        sources = [source]  # type: ignore
        total = 1

    if maximum_frames >= total:
        modulus = 1.0
    elif maximum_frames:
        modulus = max(1.0, round(total / maximum_frames, 1))
    else:
        scale = min(2.0, settings.DEFAULT_SIZE[1] / size[1] if size[1] else 1.0)
        modulus = max(1.0, round(total / (settings.MAXIMUM_FRAMES * scale), 1))

    if any(
        (
            size[0] and size[0] <= settings.PREVIEW_SIZE[0],
            size[1] and size[1] <= settings.PREVIEW_SIZE[1],
        )
    ) and not (is_preview or settings.DEBUG):
        watermark = ""

    for index, frame in enumerate(sources):
        if (index % modulus) >= 1:
            continue

        stream = io.BytesIO()
        frame.save(stream, format="GIF")
        background = Image.open(stream).convert("RGBA")
        image = resize_image(background, *size, pad, expand=False)
        percent_rendered = 1.0 if total == 1 else index / total

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
        ) in get_image_elements(
            template,
            lines,
            font_name,
            watermark,
            image.size,
            is_preview,
            percent_rendered,
        ):
            box = Image.new("RGBA", max_text_size)
            draw = ImageDraw.Draw(box)

            if settings.DEBUG:
                xy = (0, 0, max_text_size[0] - 1, max_text_size[1] - 1)
                outline = "orange" if text == settings.PREVIEW_TEXT else "lime"
                draw.rectangle(xy, outline=outline)

            rows = text.count("\n") + 1
            draw.text(
                (-offset[0], -offset[1]),
                text,
                text_fill,
                font,
                spacing=-offset[1] / (rows * 2),
                # TODO: Match to text align
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
            image = add_watermark(image, watermark, is_preview, index, total)
        elif 1 < total <= 5:
            image = add_watermark(image, ".", is_preview, index, total)

        if settings.DEBUG:
            image = add_counter(image, index, total, modulus, duration)

        frames.append(image)

    if len(frames) > settings.MINIMUM_FRAMES:
        logger.info(f"Adjusting duration of {duration} from {total} base frame(s)")
        ratio = len(frames) / max(total, settings.MAXIMUM_FRAMES)
        duration = min(250, duration // ratio)

    return frames, duration


def resize_image(
    image: ImageType, width: int, height: int, pad: bool, *, expand: bool
) -> ImageType:
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
        if expand:
            size = default_width, int(default_height / ratio)
        else:
            size = int(default_width * ratio), default_height
    else:
        if expand:
            size = int(default_width * ratio), default_height
        else:
            size = default_width, int(default_height / ratio)

    image = image.resize(size, Image.LANCZOS)
    return image


def fit_image(width: float, height: float) -> tuple[int, int]:
    while width * height > settings.MAXIMUM_PIXELS:
        width *= 0.75
        height *= 0.75
    return int(width), int(height)


def add_blurred_background(
    foreground: ImageType, background: ImageType, width: int, height: int
) -> ImageType:
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


def add_watermark(
    image: ImageType, text: str, is_preview: bool, index: int = 0, total: int = 1
) -> ImageType:
    size = (image.size[0], 1 if len(text) == 1 else settings.WATERMARK_HEIGHT)
    font = get_font("tiny", text, size, 99)
    offset = get_text_offset(text, font, size)

    watermark = Text.get_error() if is_preview else Text.get_watermark()
    stroke_width = get_stroke_width(font)
    stroke_width, stroke_fill = watermark.get_stroke(stroke_width)

    if total == 1 or total >= settings.MAXIMUM_FRAMES:
        fuzz = 0
    elif index / total < 0.5:
        fuzz = index
    else:
        fuzz = total - index - 1

    box = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(box)
    draw.text(
        (3 + fuzz, image.size[1] - size[1] - offset[1]),
        text,
        watermark.color,
        font,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )

    return Image.alpha_composite(image, box)


def add_counter(
    image: ImageType, index: int, total: int, modulus: float, duration: int
) -> ImageType:
    size = (image.size[0], settings.WATERMARK_HEIGHT)
    text = f"{index+1:02} of {total:02} / {modulus} @ {duration}"
    font = get_font("tiny", text, size, 99)

    box = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(box)
    draw.text((3, -3), text, "lime", font, stroke_width=1, stroke_fill="black")

    return Image.alpha_composite(image, box)


def get_image_elements(
    template: Template,
    lines: list[str],
    font_name: str,
    watermark: str,
    image_size: Dimensions,
    is_preview: bool = False,
    percent_rendered: float = 1.0,
) -> Iterator[tuple[Point, Offset, str, Dimensions, str, FontType, int, str, float]]:
    for index, text in enumerate(template.text):
        if percent_rendered == 1.0:
            yield get_image_element(
                lines, index, text, font_name, image_size, watermark
            )
        elif text.start <= percent_rendered < text.stop or not text.stop:
            yield get_image_element(
                lines, index, text, font_name, image_size, watermark
            )
        else:
            yield get_image_element([], index, text, font_name, image_size, watermark)
    if is_preview:
        lines = [settings.PREVIEW_TEXT]
        index = 0
        text = Text.get_preview()
        yield get_image_element(lines, index, text, "", image_size, watermark)


def get_image_element(
    lines: list[str],
    index: int,
    text: Text,
    font_name: str,
    image_size: Dimensions,
    watermark: str,
) -> tuple[Point, Offset, str, Dimensions, str, FontType, int, str, float]:
    point = text.get_anchor(image_size, watermark)

    max_text_size = text.get_size(image_size)
    max_font_size = int(image_size[1] / (4 if text.angle else 9))

    try:
        line = lines[index]
    except IndexError:
        line = ""
    else:
        line = text.stylize(
            wrap(font_name or text.font, line, max_text_size, max_font_size),
            lines=lines,
        )

    font = get_font(font_name or text.font, line, max_text_size, max_font_size)
    offset = get_text_offset(line, font, max_text_size, text.align)

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


def wrap(font: str, line: str, max_text_size: Dimensions, max_font_size: int) -> str:
    lines_1 = line
    lines_2 = split_2(line)
    lines_3 = split_3(line)

    font_1 = get_font(font, lines_1, max_text_size, max_font_size)
    font_2 = get_font(font, lines_2, max_text_size, max_font_size)
    font_3 = get_font(font, lines_3, max_text_size, max_font_size)

    if font_1.size == font_2.size and font_2.size <= settings.MINIMUM_FONT_SIZE:
        return lines_2

    if font_1.size >= font_2.size:
        return lines_1

    if get_text_size(lines_3, font_3)[0] >= max_text_size[0] * 0.60:
        return lines_3

    if get_text_size(lines_2, font_2)[0] >= max_text_size[0] * 0.60:
        return lines_2

    return lines_1


def split_2(line: str) -> str:
    midpoint = len(line) // 2 - 1

    for offset in range(0, len(line) // 4):
        for index in [midpoint - offset, midpoint + offset]:
            if line[index] == " ":
                return line[:index].strip() + "\n" + line[index:].strip()

    return line


def split_3(line: str) -> str:
    max_len = len(line) / 3
    words = line.split(" ")
    lines = ["", "", ""]
    index = 0

    for word in words:
        current_len = len(lines[index])
        next_len = current_len + len(word) * 0.7
        if next_len > max_len:
            if index < 2:
                index += 1

        lines[index] += word + " "

    return "\n".join(lines).strip()


def get_font(
    name: str, text: str, max_text_size: Dimensions, max_font_size: int
) -> FontType:
    font_path = Font.objects.get(name or settings.DEFAULT_FONT).path
    max_text_width = max_text_size[0] - max_text_size[0] / 35
    max_text_height = max_text_size[1] - max_text_size[1] / 10

    for size in range(max(settings.MINIMUM_FONT_SIZE, max_font_size), 6, -1):
        font = ImageFont.truetype(str(font_path), size=size)
        text_width, text_height = get_text_size_minus_font_offset(text, font)
        if text_width <= max_text_width and text_height <= max_text_height:
            break

    return font


def get_text_size_minus_font_offset(text: str, font: FontType) -> Dimensions:
    text_width, text_height = get_text_size(text, font)
    offset = font.getoffset(text)
    return text_width - offset[0], text_height - offset[1]


def get_text_offset(
    text: str, font: FontType, max_text_size: Dimensions, align: str = "center"
) -> Offset:
    text_size = get_text_size(text, font)
    stroke_width = get_stroke_width(font)

    x_offset, y_offset = font.getoffset(text)

    x_offset -= stroke_width
    y_offset -= stroke_width

    lines = text.split("\n")
    rows = len(lines)
    if rows >= 3:
        y_adjust = 1.1
    else:
        y_adjust = 1 + (3 - rows) * 0.25

    if align != "start":
        x_offset -= (max_text_size[0] - text_size[0]) / 2  # type: ignore
    y_offset -= (max_text_size[1] - text_size[1] / y_adjust) / 2  # type: ignore

    if any(letter in lines[-1] for letter in "gjpqy"):
        descender_offset = text_size[1] // 20
        logger.debug(f"Offsetting {lines[-1]!r} by {descender_offset} pixels")
        y_offset += descender_offset

    return x_offset, y_offset


def get_text_size(text: str, font: FontType) -> Dimensions:
    image = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(image)
    text_size = draw.textsize(text, font)
    stroke_width = get_stroke_width(font)
    return text_size[0] + stroke_width, text_size[1] + stroke_width


def get_stroke_width(font: FontType) -> int:
    return min(3, max(1, font.size // 12))
