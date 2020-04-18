from PIL import Image, ImageDraw
from pathlib import Path


def render(image_path: Path, lines: str):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((10, 10), lines)
    image.save(image_path)
