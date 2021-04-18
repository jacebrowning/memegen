from pathlib import Path

import datafiles
import log
import pytest

from .. import settings
from ..models import Template, Text


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


def describe_template():
    @pytest.fixture
    def template():
        return Template.objects.get("_test")

    def describe_str():
        def it_includes_the_path(expect, template):
            expect(str(template)).endswith("/memegen/templates/_test")

    def describe_valid():
        def it_removes_invalid_styles(expect, template, monkeypatch):
            monkeypatch.setattr(datafiles.settings, "HOOKS_ENABLED", False)
            template.styles = ["default", "sample", "unknown"]
            with (template.directory / "sample.jpg").open("w") as f:
                f.write("")
            log.info(f"{template} valid: {template.valid}")
            expect(template.styles) == ["sample"]

        def it_skips_cleanup_when_deployed(expect, template, monkeypatch):
            monkeypatch.setattr(settings, "DEPLOYED", True)
            monkeypatch.setattr(datafiles.settings, "HOOKS_ENABLED", False)
            template.styles = ["anything"]
            log.info(f"{template} valid: {template.valid}")
            expect(template.styles) == ["anything"]

    def describe_text():
        def it_defaults_to_two_lines(expect, template):
            expect(template.text) == [Text(), Text(anchor_x=0.0, anchor_y=0.8)]

    def describe_image():
        def it_has_generic_extension_when_absent(expect, template):
            expect(template.image) == Path.cwd() / "templates" / "_test" / "default.img"

        def it_creates_template_directory_automatically(expect):
            template = Template.objects.get_or_create("_custom-empty")
            template.datafile.path.unlink(missing_ok=True)
            template.datafile.path.parent.rmdir()
            log.info(template.image)
            expect(template.datafile.path.parent.exists()) == True

    def describe_create():
        @pytest.mark.asyncio
        async def it_downloads_the_image(expect):
            url = "https://www.gstatic.com/webp/gallery/1.jpg"
            path = (
                Path.cwd()
                / "templates"
                / "_custom-2d3c91e23b91d6387050e85efc1f3acb39b5a95d"
                / "default.jpg"
            )
            template = await Template.create(url, force=True)
            expect(template.image) == path
            expect(template.image.exists()) == True

        @pytest.mark.asyncio
        async def it_handles_missing_urls(expect):
            url = "http://example.com/does_not_exist.png"
            template = await Template.create(url)
            expect(template.image.exists()) == False

        @pytest.mark.asyncio
        async def it_handles_unreachable_urls(expect):
            url = "http://127.0.0.1/does_not_exist.png"
            template = await Template.create(url)
            expect(template.image.exists()) == False

        @pytest.mark.asyncio
        async def it_handles_invalid_urls(expect):
            url = "httpshttps://cdn.pixabay.com/photo/2015/09/09/19/41/cat-932846_1280.jpg"
            template = await Template.create(url)
            expect(template.image.exists()) == False

        @pytest.mark.asyncio
        async def it_rejects_non_images(expect):
            url = "https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_480_1_5MG.mp4"
            template = await Template.create(url)
            expect(template.image.exists()) == False

        @pytest.mark.asyncio
        async def it_handles_builtin_templates(expect):
            url = "http://api.memegen.link/images/fry.png"
            template = await Template.create(url)
            expect(template.id) == "fry"

        @pytest.mark.asyncio
        async def it_handles_invalid_builtin_templates(expect):
            url = "http://api.memegen.link/images/fry2.png"
            template = await Template.create(url)
            expect(template.id) == "_error"

        @pytest.mark.asyncio
        async def it_handles_custom_templates(expect):
            url = "http://api.memegen.link/images/custom.png?background=https://www.gstatic.com/webp/gallery/1.jpg"
            template = await Template.create(url)
            expect(template.id) == "_custom-2d3c91e23b91d6387050e85efc1f3acb39b5a95d"

        @pytest.mark.asyncio
        async def it_handles_meme_urls(expect):
            url = "http://api.memegen.link/images/fry/test.png"
            template = await Template.create(url)
            expect(template.id) == "fry"

    def describe_check():
        @pytest.mark.asyncio
        async def it_determines_overlay_file_extension(expect):
            url = "https://i.guim.co.uk/img/media/8a13052d4db7dcd508af948e5db7b04598e03190/0_294_5616_3370/master/5616.jpg?width=1200&height=1200&quality=85&auto=format&fit=crop&s=bcaa4eed2c1e6dab61c41a61e41433d9"
            template = Template.objects.get("fine")
            expect(await template.check(url, force=True)) == True

        @pytest.mark.asyncio
        async def it_assumes_extension_when_unknown(expect):
            url = "https://camo.githubusercontent.com/ce9c7a173f38722e129d5ae832a11c928ff72683fae74cbcb9fff41fd9957e63/68747470733a2f2f75706c6f61642e77696b696d656469612e6f72672f77696b6970656469612f636f6d6d6f6e732f7468756d622f332f33662f4769745f69636f6e2e7376672f3130323470782d4769745f69636f6e2e7376672e706e67"
            template = Template.objects.get("fine")
            expect(await template.check(url, force=True)) == True
