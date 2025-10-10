from pathlib import Path

import datafiles
import pytest
from sanic.log import logger

from ..models import Overlay, Template, Text


def describe_template():
    @pytest.fixture
    def template():
        t = Template.objects.get("_test")
        t.clean()
        yield t
        t.clean()

    def describe_str():
        def it_includes_the_path(expect, template):
            expect(str(template)).endswith("/memegen/templates/_test")

    def describe_valid():
        def it_only_includes_default_style_with_custom_overlay(
            expect, template, monkeypatch
        ):
            monkeypatch.setattr(datafiles.settings, "HOOKS_ENABLED", False)

            template.overlay = [Overlay()]
            expect(template.styles) == []

            del template.styles
            template.overlay[0].center_x = 0.123
            expect(template.styles) == ["default"]

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
            logger.info(f"{template.image=}")
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
        @pytest.mark.parametrize(
            "url",
            [
                "httpshttps://cdn.pixabay.com/photo/2015/09/09/19/41/cat-932846_1280.jpg",
                "https://https://i.imgur.com/bf995.gif&width=400",
            ],
        )
        async def it_handles_invalid_urls(expect, url):
            template = await Template.create(url)
            expect(template.valid) == False

        @pytest.mark.asyncio
        async def it_rejects_non_images(expect):
            url = "https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_480_1_5MG.mp4"
            template = await Template.create(url)
            expect(template.image.exists()) == False

        @pytest.mark.asyncio
        @pytest.mark.parametrize("subdomain", ["api", "staging"])
        async def it_handles_builtin_templates(expect, subdomain):
            url = f"http://{subdomain}.memegen.link/images/fry.png"
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
        async def it_handles_custom_templates_lacking_background(expect):
            url = "http://api.memegen.link/images/custom.png?background"
            template = await Template.create(url)
            expect(template.id) == "_error"

        @pytest.mark.asyncio
        async def it_handles_custom_templates_with_invalid_background(expect):
            url = "http://api.memegen.link/images/custom.png?background=https://https://example.com"
            template = await Template.create(url)
            expect(template.id) == "_error"

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
        async def it_accepts_multiple_urls(expect):
            style = ",".join(
                [
                    "https://www.gstatic.com/webp/gallery/1.jpg",
                    "https://www.gstatic.com/webp/gallery/2.jpg",
                ]
            )
            template: Template = Template.objects.get("perfection")
            expect(await template.check(style)) == True

        @pytest.mark.asyncio
        async def it_accepts_default_style_as_placeholder(expect):
            style = "default,https://www.gstatic.com/webp/gallery/1.jpg"
            template = Template.objects.get("perfection")
            expect(await template.check(style)) == True
