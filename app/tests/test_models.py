import pytest

from ..models import Template, Text


def describe_text():
    def describe_stylize():
        @pytest.mark.parametrize(
            ("style", "before", "after"),
            [
                ("none", "Hello, world!", "Hello, world!"),
                ("upper", "Hello, world!", "HELLO, WORLD!"),
                ("lower", "Hello, world!", "hello, world!"),
                ("title", "these are words", "These Are Words"),
                ("capitalize", "these are words", "These are words"),
                ("mock", "these are words", "ThEsE aRe WorDs"),
                ("<unknown>", "Hello, world!", "Hello, world!"),
                ("", "Hello, world!", "HELLO, WORLD!"),
            ],
        )
        def it_applies_style(expect, style, before, after):
            text = Text()
            text.style = style
            expect(text.stylize(before)) == after


def describe_template():
    def describe_create():
        @pytest.mark.asyncio
        async def it_downloads_the_image(expect):
            url = "https://www.gstatic.com/webp/gallery/1.jpg"
            template = await Template.create(url)
            expect(str(template.image)).endswith(
                "/templates/_custom-2d3c91e23b91d6387050e85efc1f3acb39b5a95d/default.img"
            )
