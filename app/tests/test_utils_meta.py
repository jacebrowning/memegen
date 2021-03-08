import pytest

from .. import utils


def describe_tokenize():
    @pytest.mark.asyncio
    async def it_restricts_sample_api_key_usage(expect, request):
        request.headers = {}
        request.args = {"api_key": "myapikey"}
        url, updated = await utils.meta.tokenize(
            request, "http://api.memegen.link/images/fry/test.png?api_key=myapikey"
        )
        expect(url) == "http://api.memegen.link/images/fry/test.png"
        expect(updated) == True
