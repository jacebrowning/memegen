import shutil

import log
import pytest

from .. import helpers, images, models, settings, text


@pytest.fixture(scope="session")
def images_directory():
    path = settings.TEST_IMAGES_DIRECTORY
    shutil.rmtree(path)
    path.mkdir()
    return path


@pytest.mark.parametrize(("key", "lines"), settings.TEST_IMAGES)
def test_images(images_directory, key, lines):
    log.info(f"Generating test image: {key}, {lines}")
    slug = text.encode_slug(lines)
    path = images_directory / key / f"{slug}.jpg"
    helpers.save_image(key, slug, root=images_directory)
