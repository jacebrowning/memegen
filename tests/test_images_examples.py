"""Tests for image generation."""

# pylint: disable=bad-continuation

from pathlib import Path

import pytest

from memegen.settings import get_config


SAMPLES = Path(__file__).parent.joinpath("examples")


def unset(name):
    config = get_config('test')
    if getattr(config, name):
        return dict(condition=False, reason="")
    else:
        return dict(condition=True, reason="{} unset".format(name))


def save_image(client, url, name):
    response = client.get(url)
    data = response.get_data()

    with SAMPLES.joinpath(name).open('wb') as image:
        image.write(data)


@pytest.mark.skipif(**unset('REGENERATE_IMAGES'))
def test_text_wrapping(client):
    """Create various example images for manual verification."""
    for name, url in [
        ("text-short.jpg", "/ch/hello/world.jpg"),
        ("text-short-on-tall.jpg", "/drake/tabs/spaces.jpg"),
        ("text-nominal.jpg", "/ch/a_normal_line_of_top_meme_text_followed_by/"
            "another_normal_line_of_bottom_meme_text.jpg"),
        ("text-long.jpg", "/ch/" + ("long_" * 15) + "line/short_line.jpg"),
        ("text-subscripts.jpg", "/ch/some_unicode_subscripts/h%E2%82%82o.jpg"),
    ]:
        save_image(client, url + "?watermark=none", name)


@pytest.mark.skipif(**unset('REGENERATE_IMAGES'))
def test_standard_font(client):
    """Create a meme using the standard meme font.

    See: https://github.com/jacebrowning/memegen/issues/216

    """
    url = "/ch/we_like_using_the/custom_fonts.jpg?font=impact&watermark=none"
    save_image(client, url, "font-impact.jpg")


@pytest.mark.skipif(**unset('REGENERATE_IMAGES'))
def test_japanese_font(client):
    """Create a meme using a font that supports Japanese characters."""
    url = "/ch/turning/日本語.jpg?font=notosanscjkjp-black&watermark=none"
    save_image(client, url, "font-notosans.jpg")


@pytest.mark.skipif(**unset('REGENERATE_IMAGES'))
def test_custom_sizes(client):
    """Create memes using custom sizes."""
    for name, url in [
        ("size-width.jpg", "/fry/hello/world.jpg?width=200"),
        ("size-height.jpg", "/fry/hello/world.jpg?height=300"),
        ("size-both.jpg", "/fry/hello/world.jpg?width=200&height=300"),
        ("size-large.jpg", "/fry/hello/world.jpg?height=1000"),
    ]:
        save_image(client, url + "&watermark=none", name)


@pytest.mark.skipif(**unset('REGENERATE_IMAGES'))
def test_custom_watermark(client):
    """Create meme with a watermark."""
    for name, partial in [
        ("watermark.jpg", "/fry/hello/world.jpg?"),
        ("watermark-pad-h.jpg", "/fry/hello/world.jpg?width=300&height=200&"),
        ("watermark-pad-v.jpg", "/fry/hello/world.jpg?width=200&height=300&"),
    ]:
        save_image(client, partial + "watermark=memegen.test", name)
