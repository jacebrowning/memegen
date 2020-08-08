import shutil

import pytest

from .. import helpers, models, settings, utils


@pytest.fixture(scope="session")
def images():
    path = settings.TEST_IMAGES_DIRECTORY
    shutil.rmtree(path)
    path.mkdir()
    return path


@pytest.mark.parametrize(("key", "lines"), settings.TEST_IMAGES)
def test_png_images(images, key, lines):
    slug = utils.text.encode(lines)
    helpers.save_image(key, slug, "png", directory=images)


def test_jpg_images(images):
    key, lines = settings.TEST_IMAGES[0]
    slug = utils.text.encode(lines)
    helpers.save_image(key, slug, "jpg", directory=images)


@pytest.mark.asyncio
async def test_custom_template(images):
    url = "https://www.gstatic.com/webp/gallery/2.jpg"
    template = await models.Template.create(url)
    utils.images.save(template, ["", "Custom Template"], directory=images)


def test_unknown_template(images):
    helpers.save_image("unknown", "unknown_template", directory=images)
