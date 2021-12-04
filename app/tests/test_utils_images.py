import os
import shutil
import time
from pathlib import Path

import pytest

from .. import models, settings, utils


@pytest.fixture(scope="session")
def images():
    path = settings.TEST_IMAGES_DIRECTORY

    flag = path / ".flag"
    if flag.exists():
        age = time.time() - flag.stat().st_mtime
        if age > 60 * 60 * 6 and "SKIP_SLOW" not in os.environ:
            shutil.rmtree(path)

    path.mkdir(exist_ok=True)
    flag.touch()

    return path


@pytest.fixture(scope="session")
def template():
    return models.Template.objects.get("icanhas")


# Formats


@pytest.mark.slow
@pytest.mark.parametrize(("id", "lines", "extension"), settings.TEST_IMAGES)
def test_images(images, id, lines, extension):
    template = models.Template.objects.get(id)
    utils.images.save(template, lines, extension=extension, directory=images)


# Size


def test_smaller_width(images, template):
    utils.images.save(template, ["width=250"], size=(250, 0), directory=images)


def test_smaller_height(images, template):
    utils.images.save(template, ["height=250"], size=(0, 250), directory=images)


def test_larger_width(images, template):
    utils.images.save(template, ["width=500"], size=(500, 0), directory=images)


def test_larger_height(images, template):
    utils.images.save(template, ["height=500"], size=(0, 500), directory=images)


def test_wide_padding(images, template):
    lines = ["width=600", "height=400"]
    utils.images.save(template, lines, size=(600, 400), directory=images)


def test_tall_padding(images, template):
    lines = ["width=400", "height=600"]
    utils.images.save(template, lines, size=(400, 600), directory=images)


def test_small_padding(images, template):
    lines = ["width=50", "height=50"]
    utils.images.save(template, lines, size=(50, 50), directory=images)


@pytest.mark.slow
def test_large_padding(images, template):
    lines = ["width=2000", "height=2000"]
    utils.images.save(template, lines, size=(2000, 2000), directory=images)


# Templates


@pytest.mark.asyncio
async def test_custom_template(images):
    url = "https://www.gstatic.com/webp/gallery/2.jpg"
    template = await models.Template.create(url)
    utils.images.save(template, ["", "My Custom Template"], directory=images)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_custom_template_with_exif_rotation(images):
    url = "https://cdn.discordapp.com/attachments/752902976322142218/752903391281283152/20200608_111430.jpg"
    template = await models.Template.create(url)
    utils.images.save(template, ["", "This should not be rotated!"], directory=images)


def test_unknown_template(images):
    template = models.Template.objects.get("_error")
    utils.images.save(template, ["UNKNOWN TEMPLATE"], directory=images)


# Styles


@pytest.mark.slow
def test_alternate_style(images):
    template = models.Template.objects.get("ds")
    lines = ["one", "two", "three"]
    utils.images.save(template, lines, style="maga", directory=images)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_custom_style(images):
    url = "https://sn56.scholastic.com/content/dam/classroom-magazines/sn56/issues/2019-20/031620/coronavirus/16-SN56-20200316-VirusOutbreak-PO-2.png"
    template = models.Template.objects.get("fine")
    await template.check(url, force=True)
    lines = ["102 °F", "this is fine"]
    utils.images.save(template, lines, style=url, directory=images)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_custom_style_rotated(images):
    style = "https://i.imgur.com/6hwAxmO.jpg,https://i.imgur.com/6hwAxmO.jpg"
    template = models.Template.objects.get("same")
    await template.check(style, force=True)
    utils.images.save(template, [], style=style, directory=images)


# Text


def test_special_characters(images, template):
    lines = ["Special? 100% #these-memes", "template_rating: 9/10"]
    utils.images.save(template, lines, directory=images)


@pytest.mark.skipif("CIRCLECI" in os.environ, reason="Long filenames not supported")
def test_extremely_long_text(images, tmpdir):
    template = models.Template.objects.get("fry")
    lines = ["", "word " * 40]
    utils.images.save(template, lines, directory=Path(tmpdir) / "images")


def test_long_first_word(images):
    template = models.Template.objects.get("fine")
    lines = ["", "thiiiiiiiiiiiiiiiiiiiiis will probably be fine right now"]
    utils.images.save(template, lines, directory=images)


@pytest.mark.slow
def test_text_wrap_when_font_is_too_small(images):
    template = models.Template.objects.get("ds")
    lines = ["this button seems to be ok to push"]
    utils.images.save(template, lines, directory=images)


def test_text_wrap_on_small_images(images):
    template = models.Template.objects.get("pigeon")
    lines = ["", "multiple words here"]
    utils.images.save(template, lines, size=(0, 300), directory=images)


def test_text_wrap_on_smaller_images(images):
    template = models.Template.objects.get("toohigh")
    lines = ["", "the number of sample memes is too damn high!"]
    utils.images.save(template, lines, size=(0, 200), directory=images)


@pytest.mark.slow
def test_descender_vertical_alignment(images):
    template = models.Template.objects.get("ptj")
    lines = [
        "Exit",
        "Exit",
        "the",
        "the",
        "monorepo",
        "monorepo",
        "Exit the monorepo.",
        "Stop testing!",
    ]
    utils.images.save(template, lines, directory=images)


# Watermark


def test_watermark(images, template):
    lines = ["nominal image", "with watermark"]
    utils.images.save(template, lines, "Example.com", directory=images)


def test_watermark_with_padding(images, template):
    lines = ["paddded image", "with watermark"]
    utils.images.save(template, lines, "Example.com", size=(500, 500), directory=images)


def test_watermark_disabled_when_small(images, template):
    lines = ["small image", "with watermark (disabled)"]
    utils.images.save(template, lines, "Example.com", size=(300, 0), directory=images)


@pytest.mark.slow
def test_watermark_with_many_lines(images):
    template = models.Template.objects.get("ptj")
    lines = ["", "", "", "", "", "", "Has a watermark.", "Doesn't have a watermark!"]
    utils.images.save(template, lines, "Example.com", directory=images)


# Debug


@pytest.mark.parametrize(("extension"), ["png", "gif"])
def test_debug_images(images, monkeypatch, extension):
    monkeypatch.setattr(settings, "DEBUG", True)

    id, lines, _extension = settings.TEST_IMAGES[0]
    template = models.Template.objects.get(id)
    lines = [lines[0], lines[1] + " (debug)"]
    utils.images.save(template, lines, directory=images)
    utils.images.save(template, lines, directory=images, extension=extension)


def test_deployed_images(images, monkeypatch):
    monkeypatch.setattr(settings, "DEPLOYED", True)

    id, lines, _extension = settings.TEST_IMAGES[0]
    template = models.Template.objects.get(id)
    utils.images.save(template, lines, directory=images)

    monkeypatch.delattr(utils.images, "render_image")
    utils.images.save(template, lines, directory=images)


def test_preview_images(images, template):
    path = images / "preview.jpg"
    data, _extension = utils.images.preview(template, ["nominal image", "while typing"])
    path.write_bytes(data)
