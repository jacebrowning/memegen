import pytest

from .. import utils

LINES_SLUG = [(["?%#/"], "~q~p~h~s"), (["a/b", "c"], "a~sb/c")]


@pytest.mark.parametrize(("lines", "slug"), LINES_SLUG)
def test_encode(expect, lines, slug):
    expect(utils.text.encode(lines)) == slug


@pytest.mark.parametrize(("lines", "slug"), LINES_SLUG)
def test_decode(expect, lines, slug):
    expect(utils.text.decode(slug)) == lines
