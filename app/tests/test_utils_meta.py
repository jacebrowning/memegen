import pytest

from .. import settings, utils


def describe_tokenize():
    @pytest.mark.asyncio
    async def it_restricts_sample_api_key_usage(expect, request):
        request.args = {"api_key": "myapikey42"}
        request.headers = {}

        url, updated = await utils.meta.tokenize(
            request, "http://api.memegen.link/images/fry/test.png?api_key=myapikey42"
        )

        expect(url) == "http://api.memegen.link/images/fry/test.png"
        expect(updated) == True


def describe_track():
    @pytest.mark.asyncio
    async def it_is_disabled_automatically_after_error(expect, monkeypatch, request):
        monkeypatch.setattr(settings, "REMOTE_TRACKING_URL", "http://example.com/404")
        request.args = {}
        request.headers = {}
        request.url = "http://example.com"

        await utils.meta.track(request, ["foo", "bar"])

        expect(settings.TRACK_REQUESTS) == False
