from contextlib import asynccontextmanager

import pytest
from aiohttp import web
from anyio import Path as AsyncPath

from .. import settings, utils

CONTENT = b"x" * 2000


@asynccontextmanager
async def server():
    async def image(request):
        return web.Response(body=CONTENT, content_type="image/png")

    async def stream(request):
        response = web.StreamResponse(headers={"Content-Type": "image/png"})
        response.enable_chunked_encoding()
        await response.prepare(request)
        for _ in range(4):
            await response.write(CONTENT)
        await response.write_eof()
        return response

    async def redirect_local(request):
        raise web.HTTPFound("/image.png")

    async def redirect_private(request):
        raise web.HTTPFound("http://10.255.255.1/image.png")

    app = web.Application()
    app.router.add_get("/image.png", image)
    app.router.add_get("/stream.png", stream)
    app.router.add_get("/redirect-local", redirect_local)
    app.router.add_get("/redirect-private", redirect_private)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    try:
        yield f"http://127.0.0.1:{port}", port
    finally:
        await runner.cleanup()


@pytest.fixture
def allow_loopback(monkeypatch):
    monkeypatch.setattr(
        utils.http, "is_public_address", lambda address: address.startswith("127.")
    )


def describe_is_public_address():
    @pytest.mark.parametrize("address", ["8.8.8.8", "2001:4860:4860::8888"])
    def it_allows_public_addresses(expect, address):
        expect(utils.http.is_public_address(address)) == True

    @pytest.mark.parametrize(
        "address",
        [
            "127.0.0.1",
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
            "169.254.169.254",
            "100.64.0.1",
            "0.0.0.0",
            "224.0.0.1",
            "::1",
            "fd00::1",
            "fe80::1",
            "::ffff:127.0.0.1",
            "not-an-address",
        ],
    )
    def it_rejects_non_public_addresses(expect, address):
        expect(utils.http.is_public_address(address)) == False


def describe_is_public_url():
    def it_defers_hostnames_to_the_resolver(expect):
        expect(utils.http.is_public_url("https://example.com/a.png")) == True

    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1/a.png",
            "http://[::1]/a.png",
            "http://169.254.169.254/latest/meta-data/",
            "not a url",
        ],
    )
    def it_rejects_non_public_hosts(expect, url):
        expect(utils.http.is_public_url(url)) == False


def describe_download():
    @pytest.mark.asyncio
    async def it_refuses_loopback_addresses(expect, tmp_path):
        path = AsyncPath(tmp_path / "default.png")
        async with server() as (base, _port):
            expect(await utils.http.download(f"{base}/image.png", path)) == False
        expect(await path.exists()) == False

    @pytest.mark.asyncio
    async def it_refuses_hostnames_resolving_to_private_addresses(expect, tmp_path):
        path = AsyncPath(tmp_path / "default.png")
        async with server() as (_base, port):
            url = f"http://localhost:{port}/image.png"
            expect(await utils.http.download(url, path)) == False
        expect(await path.exists()) == False

    @pytest.mark.asyncio
    async def it_refuses_redirects_to_private_addresses(
        expect, tmp_path, allow_loopback
    ):
        path = AsyncPath(tmp_path / "default.png")
        async with server() as (base, _port):
            url = f"{base}/redirect-private"
            expect(await utils.http.download(url, path)) == False
        expect(await path.exists()) == False

    @pytest.mark.asyncio
    async def it_downloads_allowed_images(expect, tmp_path, allow_loopback):
        path = AsyncPath(tmp_path / "default.png")
        async with server() as (base, _port):
            expect(await utils.http.download(f"{base}/image.png", path)) == True
        expect(await path.read_bytes()) == CONTENT

    @pytest.mark.asyncio
    async def it_follows_allowed_redirects(expect, tmp_path, allow_loopback):
        path = AsyncPath(tmp_path / "default.png")
        async with server() as (base, _port):
            url = f"{base}/redirect-local"
            expect(await utils.http.download(url, path)) == True
        expect(await path.read_bytes()) == CONTENT

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", ["image.png", "stream.png"])
    async def it_refuses_oversized_images(
        expect, tmp_path, allow_loopback, monkeypatch, name
    ):
        monkeypatch.setattr(settings, "MAXIMUM_DOWNLOAD_SIZE", 1000)
        path = AsyncPath(tmp_path / "default.png")
        async with server() as (base, _port):
            expect(await utils.http.download(f"{base}/{name}", path)) == False
        expect(await path.exists()) == False
