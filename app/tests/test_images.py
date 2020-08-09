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


def test_debug_images(images, monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", True)
    key, lines = settings.TEST_IMAGES[0]
    template = models.Template.objects.get(key)
    lines = [lines[0], lines[1] + " (debug)"]
    utils.images.save(template, lines, directory=images)


@pytest.mark.asyncio
async def test_custom_template(images):
    url = "https://www.gstatic.com/webp/gallery/2.jpg"
    template = await models.Template.create(url)
    utils.images.save(template, ["", "Custom Template"], directory=images)


def test_unknown_template(images):
    template = models.Template.objects.get("_error")
    utils.images.save(template, ["UNKNOWN TEMPLATE"], directory=images)


def test_special_characters(images):
    template = models.Template.objects.get("fry")
    lines = ["Special? 100% #these-memes", "template_rating: 9/10"]
    utils.images.save(template, lines, directory=images)


def test_extremely_long_text(images):
    template = models.Template.objects.get("fry")
    lines = ["", "word " * 50]
    utils.images.save(template, lines, directory=images)
