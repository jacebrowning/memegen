import os

from PIL import Image as ImageFile, ImageFont, ImageDraw


FONT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'fonts', 'Impact.ttf'))


class Image:
    """Meme image generated from a template."""

    @classmethod
    def from_template(cls, template, text, kind):
        make_meme(text.top, text.bottom, template.path)
        return "../temp.jpg"


# based on: https://github.com/danieldiekmeier/memegenerator
def make_meme(topString, bottomString, filename):
    print(FONT)

    img = ImageFile.open(filename)
    imageSize = img.size

    # find biggest font size that works
    fontSize = int(imageSize[1] / 5)
    font = ImageFont.truetype(FONT, fontSize)
    topTextSize = font.getsize(topString)
    bottomTextSize = font.getsize(bottomString)
    while topTextSize[0] > imageSize[0] - 20 or bottomTextSize[0] > imageSize[0] - 20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(FONT, fontSize)
        topTextSize = font.getsize(topString)
        bottomTextSize = font.getsize(bottomString)

    # find top centered position for top text
    topTextPositionX = (imageSize[0] / 2) - (topTextSize[0] / 2)
    topTextPositionY = 0
    topTextPosition = (topTextPositionX, topTextPositionY)

    # find bottom centered position for bottom text
    bottomTextPositionX = (imageSize[0] / 2) - (bottomTextSize[0] / 2)
    bottomTextPositionY = imageSize[1] - bottomTextSize[1] - bottomTextSize[1] / 6
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)

    draw = ImageDraw.Draw(img)

    # draw outlines
    # there may be a better way
    outlineRange = int(fontSize / 15)
    for x in range(-outlineRange, outlineRange + 1):
        for y in range(-outlineRange, outlineRange + 1):
            draw.text((topTextPosition[0] + x, topTextPosition[1] + y), topString, (0, 0, 0), font=font)
            draw.text((bottomTextPosition[0] + x, bottomTextPosition[1] + y), bottomString, (0, 0, 0), font=font)

    draw.text(topTextPosition, topString, (255, 255, 255), font=font)
    draw.text(bottomTextPosition, bottomString, (255, 255, 255), font=font)

    return img.save("temp.jpg")
