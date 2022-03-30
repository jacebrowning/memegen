import pytest
from aioresponses import aioresponses

from .. import settings, utils


def describe_authenticate():
    @pytest.mark.asyncio
    async def it_returns_payload_from_tracker(expect, monkeypatch, request):
        monkeypatch.setattr(settings, "REMOTE_TRACKING_URL", "http://example.com/")
        request.args = {}

        with aioresponses() as patched_session:
            patched_session.get(
                "http://example.com/auth",
                payload={"error": "API key missing or invalid."},
            )
            patched_session.get(
                "http://example.com/auth",
                payload={"email": "user@example.com"},
            )

            request.headers = {"x-api-key": "invalid"}
            response = await utils.meta.authenticate(request)
            expect(response) == {"error": "API key missing or invalid."}

            request.headers = {"x-api-key": "valid"}
            response = await utils.meta.authenticate(request)
            expect(response) == {"email": "user@example.com"}


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

    @pytest.mark.asyncio
    async def it_returns_url_from_tracker(expect, monkeypatch, request):
        monkeypatch.setattr(settings, "REMOTE_TRACKING_URL", "http://example.com/")
        request.args = {}

        with aioresponses() as patched_session:
            patched_session.post(
                "http://example.com/tokenize",
                payload={"url": "http://example.com/foobar.png?token=abc123"},
            )

            request.headers = {"x-api-key": "valid"}
            data = await utils.meta.tokenize(request, "http://example.com/foobar.png")
            expect(data) == ("http://example.com/foobar.png?token=abc123", True)


def describe_track():
    @pytest.mark.asyncio
    async def it_is_disabled_automatically_after_error(expect, monkeypatch, request):
        monkeypatch.setattr(settings, "REMOTE_TRACKING_URL", "http://example.com/404")
        monkeypatch.setattr(settings, "REMOTE_TRACKING_ERRORS_LIMIT", 1)
        request.args = {}
        request.headers = {}
        request.host = "example.com"
        request.url = "http://example.com"

        await utils.meta.track(request, ["foobar"])
        await utils.meta.track(request, ["foobar"])

        expect(settings.TRACK_REQUESTS) == False
