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
    template = models.Template.objects.get(key)
    utils.images.save(template, lines, "png", directory=images)


def test_jpg_images(images):
    key, lines = settings.TEST_IMAGES[0]
    template = models.Template.objects.get(key)
    utils.images.save(template, lines, "jpg", directory=images)


@pytest.mark.asyncio
async def test_custom_template(images):
    url = "https://www.gstatic.com/webp/gallery/2.jpg"
    template = await models.Template.create(url)
    utils.images.save(template, ["", "Custom Template"], directory=images)


def test_unknown_template(images):
    template = models.Template.objects.get("_error")
    utils.images.save(template, ["UNKNOWN TEMPLATE"], directory=images)
