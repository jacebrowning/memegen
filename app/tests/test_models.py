from pathlib import Path

import pytest

from .. import settings
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


def describe_template():
    def describe_text():
        def it_defaults_to_two_lines(expect):
            template = Template.objects.get("_test")
            expect(template.text) == [Text(), Text(anchor_x=0.05, anchor_y=0.75)]

    def describe_image():
        def it_has_generic_extension_when_absent(expect):
            template = Template.objects.get("_test")
            expect(template.image) == Path.cwd() / "templates" / "_test" / "default.img"

    def describe_create():
        @pytest.mark.asyncio
        async def it_downloads_the_image(expect, monkeypatch):
            monkeypatch.setattr(settings, "DEBUG", True)
            url = "https://www.gstatic.com/webp/gallery/1.jpg"
            path = (
                Path.cwd()
                / "templates"
                / "_custom-2d3c91e23b91d6387050e85efc1f3acb39b5a95d"
                / "default.img"
            )
            template = await Template.create(url)
            expect(template.image) == path
            expect(template.image.exists()) == True

        @pytest.mark.asyncio
        async def it_handles_invalid_urls(expect):
            url = "http://example.com/does_not_exist.png"
            template = await Template.create(url)
            expect(template.image.exists()) == False
