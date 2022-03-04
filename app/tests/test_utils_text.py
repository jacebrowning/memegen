import pytest

from .. import utils

LINES_SLUG = [
    (["hello world"], "hello_world"),
    (["?%#/&\\<>"], "~q~p~h~s~a~b~l~g"),
    (["a/b", "c"], "a~sb/c"),
    (["variable_name"], "variable__name"),
    (["variable-name"], "variable--name"),
    (["foo\nbar"], "foo~nbar"),
    (["def data() -> Dict"], "def_data()_--~g_Dict"),
    (["finish <- start"], "finish_~l--_start"),
    (['That\'s not how "this" works'], "That's_not_how_''this''_works"),
    (["git commit --no-verify"], "git_commit_----no--verify"),
    (["_username likes _charname"], "__username_likes___charname"),
]


@pytest.mark.parametrize(("lines", "slug"), LINES_SLUG)
def test_encode(expect, lines, slug):
    expect(utils.text.encode(lines)) == slug


@pytest.mark.parametrize(("lines", "slug"), LINES_SLUG)
def test_decode(expect, lines, slug):
    expect(utils.text.decode(slug)) == lines


def test_decode_dashes(expect):
    expect(utils.text.decode("hello-world")) == ["hello world"]


def test_encode_quotes(expect):
    expect(
        utils.text.encode(["it’ll be great “they” said"])
    ) == 'it\'ll_be_great_"they"_said'


def test_encode_dashes(expect):
    expect(utils.text.encode(["1–2 in. of snow"])) == "1-2_in._of_snow"
