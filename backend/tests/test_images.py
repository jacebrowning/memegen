import pytest

from pathlib import Path
import shutil

from .. import images, models

IMAGES = [("iw", "tests_code/in_production")]
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
    path = images_directory / "index.html"
    with path.open("w") as f:
        f.write(f'<meta http-equiv="refresh" content="60">\n')
        for key, lines in IMAGES:
            href = f"http://localhost:5001/api/images/{key}/{lines}.jpg?time=0"
            f.write(f'<img src="{href}" style="padding: 10px;">\n')
        f.write(SCRIPT)
    return path


def test_images(images_directory):
    for key, lines in IMAGES:
        template = models.Template.objects.get(key)
        image = images.render(template, lines)
        path = images_directory / key / f"{lines}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
