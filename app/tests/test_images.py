from pathlib import Path

import log
import pytest

from .. import helpers, images, models

IMAGES = [("iw", "tests_code/in_production"), ("unknown", "_/unknown template")]
SCRIPT = r"""<script>
setInterval(function() {
    var images = document.images;
    for (var i=0; i<images.length; i++) {
        images[i].src = images[i].src.replace(/\btime=[^&]*/, 'time=' + new Date().getTime());
    }
}, 2000);
</script>
"""


@pytest.fixture(scope="session")
def images_directory():
    path = Path.cwd() / "tests" / "images"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture(scope="session", autouse=True)
def index(images_directory):
    path = images_directory / ".gitignore"
    with path.open("w") as f:
        f.write("index.html\n")

    path = images_directory / "index.html"
    with path.open("w") as f:
        f.write(f'<meta http-equiv="refresh" content="60">\n')
        for key, lines in IMAGES:
            href = f"http://localhost:5000/api/images/{key}/{lines}.jpg?time=0"
            f.write(f'<img src="{href}" width="500" style="padding: 5px;">\n')
        f.write(SCRIPT)

    return path


def test_images(images_directory):
    for key, lines in IMAGES:
        log.info(f"Generating test image: {key}, {lines}")
        path = images_directory / key / f"{lines}.jpg"
        helpers.save_image(key, lines, path=path)
