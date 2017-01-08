"""Tests for image generation."""

# pylint: disable=bad-continuation

import os
from pathlib import Path

import pytest


ENV = 'REGENERATE_IMAGES'
SAMPLES = Path(__file__).parent.joinpath("examples")


def save_image(client, url, name):
    response = client.get(url)
    data = response.get_data()

    with SAMPLES.joinpath(name).open('wb') as image:
        image.write(data)


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_text(client):
    """Create various example images for manual verification."""
    for name, url in [
        ("text-basic.jpg", "/ch/hello/world.jpg"),
        ("text-nominal.jpg", "/ch/a-normal-line-of-top-meme-text-followed-by/"
            "another-normal-line-of-bottom-meme-text.jpg"),
        ("text-long.jpg", "/ch/" + ("long-" * 15) + "line/short-line.jpg"),
        ("text-subscripts.jpg", "/ch/some-unicode-subscripts/h%E2%82%82o.jpg"),
    ]:
        save_image(client, url, name)


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_standard_font(client):
    """Create a meme using the standard meme font.

    See: https://github.com/jacebrowning/memegen/issues/216

    """
    url = "/ch/we-like-using-the/custom-fonts.jpg?font=impact"
    save_image(client, url, "font-impact.jpg")


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_japanese_font(client):
    """Create a meme using a font that supports Japanese characters."""
    url = "/ch/turning/日本語.jpg?font=notosanscjkjp-black"
    save_image(client, url, "font-notosans.jpg")


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_custom_sizes(client):
    """Create memes using custom sizes."""
    for name, url in [
        ("size-width.jpg", "/older/hello/world.jpg?width=200"),
        ("size-height.jpg", "/older/hello/world.jpg?height=300"),
        ("size-both.jpg", "/older/hello/world.jpg?width=200&height=300"),
    ]:
        save_image(client, url, name)
