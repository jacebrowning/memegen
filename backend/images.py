from PIL import Image, ImageDraw


def render(template, lines: str) -> Image:
    image = Image.open(template.background_image_path)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((10, 10), lines)
    return image
