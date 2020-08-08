import pytest

from ..models import Template


def describe_template():
    def describe_create():
        @pytest.mark.asyncio
        async def it_downloads_the_image(expect):
            url = "https://www.gstatic.com/webp/gallery/1.jpg"
            template = await Template.create(url)
            expect(str(template.image)).endswith(
                "/templates/_custom-2d3c91e23b91d6387050e85efc1f3acb39b5a95d/default.img"
            )
