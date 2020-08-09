import pytest

from .. import utils

LINES_SLUG = [
    (["hello world"], "hello_world"),
    (["?%#/"], "~q~p~h~s"),
    (["a/b", "c"], "a~sb/c"),
    (["variable_name"], "variable__name"),
    (["variable-name"], "variable--name"),
]


@pytest.mark.parametrize(("lines", "slug"), LINES_SLUG)
def test_encode(expect, lines, slug):
    expect(utils.text.encode(lines)) == slug


@pytest.mark.parametrize(("lines", "slug"), LINES_SLUG)
def test_decode(expect, lines, slug):
    expect(utils.text.decode(slug)) == lines


def test_decode_dashes(expect):
    expect(utils.text.decode("hello-world")) == ["hello world"]
