from pathlib import Path

import log
import pytest

from .. import helpers, images, models

TEST_IMAGES = [("iw", "tests_code/in_production"), ("unknown", "_/unknown template")]


@pytest.fixture(scope="session")
def images_directory():
    path = Path.cwd() / "tests" / "images"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture(scope="session", autouse=True)
def index(images_directory):
    urls = [
        f"http://localhost:5000/api/images/{key}/{lines}.jpg"
        for key, lines in TEST_IMAGES
    ]
    html = helpers.display_images(urls, refresh=True)

    path = images_directory / ".gitignore"
    with path.open("w") as f:
        f.write("index.html\n")

    path = images_directory / "index.html"
    with path.open("w") as f:
        f.write(html)

    return path


def test_images(images_directory):
    for key, lines in TEST_IMAGES:
        log.info(f"Generating test image: {key}, {lines}")
        path = images_directory / key / f"{lines}.jpg"
        helpers.save_image(key, lines, path=path)
