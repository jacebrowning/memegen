"""Tests for image generation."""

# pylint: disable=bad-continuation

import os
from pathlib import Path

import pytest


ENV = 'REGENERATE_IMAGES'
SAMPLES = Path(__file__).parent.joinpath("samples")


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_samples(client):
    """Create various sample images for manual verfification."""
    for name, url in [
        ("basic.jpg", "/ch/hello/world.jpg"),
        ("nominal.jpg", "/ch/a-normal-line-of-top-meme-text-followed-by/"
            "another-normal-line-of-bottom-meme-text.jpg"),
        ("long.jpg", "/ch/" + ("long-" * 15) + "line/short-line.jpg"),
        ("subscripts.jpg", "/ch/some-unicode-subscripts/h%E2%82%82o.jpg"),
    ]:
        save_image(client, url, name)


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_standard_font(client):
    """Create a meme using the standard meme font.

    See: https://github.com/jacebrowning/memegen/issues/216

    """
    url = "/ch/we-like-using-the/custom-fonts.jpg?font=impact"
    save_image(client, url, "impact.jpg")


@pytest.mark.skipif(not os.getenv(ENV), reason="{} unset".format(ENV))
def test_japanese_font(client):
    """Create a meme using a font that supports Japanese characters."""
    url = "/ch/turning/日本語.jpg?font=notosanscjkjp-black"
    save_image(client, url, "notosans.jpg")


def save_image(client, url, name):
    response = client.get(url)
    data = response.get_data()

    with SAMPLES.joinpath(name).open('wb') as image:
        image.write(data)
