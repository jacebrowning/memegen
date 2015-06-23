import os
import logging

from PIL import Image as ImageFile, ImageFont, ImageDraw


log = logging.getLogger(__name__)

# TODO: move to a fonts store
FONT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'fonts', 'Impact.ttf')
)


class Image:
    """Meme JPEG generated from a template."""

    def __init__(self, template, text, root=None):
        self.template = template
        self.text = text
        self.root = None

    @property
    def path(self):
        if self.root:
            return os.path.join(self.root, self.template.key,
                                self.text.path + '.jpg')
        else:
            return None

    def generate(self):
        directory = os.path.dirname(self.path)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        make_meme(self.text.top, self.text.bottom,
                  self.template.path, self.path)


# based on: https://github.com/danieldiekmeier/memegenerator
def make_meme(top, bottom, background, path):
    img = ImageFile.open(background)
    image_size = img.size

    # Find biggest font size that works
    font_size = int(image_size[1] / 5)
    font = ImageFont.truetype(FONT, font_size)
    top_text_size = font.getsize(top)
    bottom_text_size = font.getsize(bottom)
    while (top_text_size[0] > image_size[0] - 20 or
           bottom_text_size[0] > image_size[0] - 20):
        font_size = font_size - 1
        font = ImageFont.truetype(FONT, font_size)
        top_text_size = font.getsize(top)
        bottom_text_size = font.getsize(bottom)

    # Find top centered position for top text
    top_text_position_x = (image_size[0] / 2) - (top_text_size[0] / 2)
    top_text_position_y = 0
    top_text_position = (top_text_position_x, top_text_position_y)

    # Find bottom centered position for bottom text
    bottom_text_size_x = (image_size[0] / 2) - (bottom_text_size[0] / 2)
    bottom_text_size_y = image_size[1] - bottom_text_size[1] * (7 / 6)
    bottom_text_position = (bottom_text_size_x, bottom_text_size_y)

    # Draw image
    draw = ImageDraw.Draw(img)

    # Draw black text outlines
    outline_range = int(font_size / 15)
    for x in range(-outline_range, outline_range + 1):
        for y in range(-outline_range, outline_range + 1):
            draw.text(
                (top_text_position[0] + x, top_text_position[1] + y), top, (0, 0, 0), font=font)
            draw.text((bottom_text_position[
                      0] + x, bottom_text_position[1] + y), bottom, (0, 0, 0), font=font)

    # Draw inner white text
    draw.text(top_text_position, top, (255, 255, 255), font=font)
    draw.text(bottom_text_position, bottom, (255, 255, 255), font=font)

    log.info("generated: {}".format(path))
    return img.save(path)
