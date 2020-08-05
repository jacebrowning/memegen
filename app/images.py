from pathlib import Path
from typing import Iterator, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from . import settings
from .models import Template
from .types import Dimensions, Point


def save(
    template: Template,
    lines: List[str],
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


def render(template: Template, lines: List[str], size: Dimensions) -> Image:
    image = Image.open(template.background_image_path)
    image = image.convert("RGB")

    image.thumbnail(size, Image.LANCZOS)

    draw = ImageDraw.Draw(image)
    for point, text, max_text_size in build(template, lines, image.size):
        if settings.SHOW_TEXT_BOXES:
            point2 = (point[0] + max_text_size[0], point[1] + max_text_size[1])
            draw.rectangle((point, point2), outline="lime")

        # TODO: try stroke_fill for outline
        font = get_font(text, max_text_size)
        # TODO: adjust for font.getoffset(text)
        draw.text(point, text, font=font)

    return image


def build(
    template: Template, lines: List[str], image_size: Dimensions
) -> Iterator[Tuple[Point, str, Dimensions]]:
    for index, text in enumerate(template.text):
        point = text.get_anchor(image_size)
        try:
            line = lines[index]
        except IndexError:
            line = ""
        size = text.get_size(image_size)
        yield point, line, size


def get_font(text: str, max_text_size: Dimensions) -> ImageFont:
    max_text_width, max_text_height = max_text_size
    for size in range(72, 5, -1):
        font = ImageFont.truetype(str(settings.FONT), size=size)
        text_width, text_height = font.getsize(text)
        if text_width <= max_text_width and text_height <= max_text_height:
            break
    return font
