import shutil

import pytest

from .. import helpers, settings, text


@pytest.fixture(scope="session")
def images_directory():
    path = settings.TEST_IMAGES_DIRECTORY
    shutil.rmtree(path)
    path.mkdir()
    return path


@pytest.mark.parametrize(("key", "lines"), settings.TEST_IMAGES)
def test_png_images(images_directory, key, lines):
    slug = text.encode_slug(lines)
    helpers.save_image(key, slug, "png", directory=images_directory)


def test_jpg_images(images_directory):
    key, lines = settings.TEST_IMAGES[0]
    slug = text.encode_slug(lines)
    helpers.save_image(key, slug, "jpg", directory=images_directory)
