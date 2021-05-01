import pytest

from ..models import Text


def describe_text():
    def describe_stylize():
        @pytest.mark.parametrize(
            ("style", "before", "after"),
            [
                ("none", "Hello, world!", "Hello, world!"),
                ("default", "these are words.", "These are words."),
                ("default", "These ARE words.", "These ARE words."),
                ("upper", "Hello, world!", "HELLO, WORLD!"),
                ("lower", "Hello, world!", "hello, world!"),
                ("title", "these are words", "These Are Words"),
                ("capitalize", "these are words", "These are words"),
                ("mock", "these are words", "ThEsE aRe WorDs"),
                ("<unknown>", "Hello, world!", "Hello, world!"),
            ],
        )
        def it_applies_style(expect, style, before, after):
            text = Text()
            text.style = style
            expect(text.stylize(before)) == after

        def it_defaults_to_upper(expect):
            text = Text()
            text.style = ""
            expect(text.stylize("Foobar")) == "FOOBAR"

        def it_respects_case_when_set_in_any_line(expect):
            text = Text(style="default")
            expect(text.stylize("foo", lines=["foo", " ", "bar"])) == "Foo"
            expect(text.stylize("foo", lines=["foo", " ", "Bar"])) == "foo"
