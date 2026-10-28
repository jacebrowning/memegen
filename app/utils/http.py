import asyncio
import ipaddress
import socket

import aiofiles
import aiohttp
import aiohttp.client_exceptions
from aiohttp.abc import AbstractResolver, ResolveResult
from aiohttp.resolver import DefaultResolver
from anyio import Path as AsyncPath
from sanic.log import logger
from yarl import URL

from .. import settings

EXCEPTIONS = (
    aiohttp.client_exceptions.ClientConnectionError,
    aiohttp.client_exceptions.InvalidURL,
    aiohttp.client_exceptions.TooManyRedirects,
    aiohttp.client_exceptions.NonHttpUrlClientError,
    aiohttp.client_exceptions.ClientResponseError,
    AssertionError,
    asyncio.TimeoutError,
    UnicodeError,
)


async def fetch(url: str, **kwargs) -> tuple[int, dict | str]:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as session:
        try:
            async with session.get(url, **kwargs) as response:
                try:
                    message = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    message = await response.text()

                return response.status, message

        except EXCEPTIONS as e:
            message = str(e).strip("() ") or e.__class__.__name__

            return 500, message


def is_public_address(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


def is_public_url(url: str) -> bool:
    try:
        host = URL(url).host
    except (ValueError, TypeError):
        return False
    if not host:
        return False
    try:
        ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        return True  # hostnames are checked by PublicResolver after lookup
    return is_public_address(host)


class PublicResolver(AbstractResolver):
    """Resolve hostnames, but only to publicly routable addresses."""

    def __init__(self):
        self._resolver = DefaultResolver()

    async def resolve(
        self, host: str, port: int = 0, family: socket.AddressFamily = socket.AF_INET
    ) -> list[ResolveResult]:
        results = await self._resolver.resolve(host, port, family)
        allowed = [result for result in results if is_public_address(result["host"])]
        if not allowed:
            raise OSError(f"{host} does not resolve to a public address")
        return allowed

    async def close(self) -> None:
        await self._resolver.close()


async def download(url: str, path: AsyncPath) -> bool:
    connector = aiohttp.TCPConnector(resolver=PublicResolver())
    async with aiohttp.ClientSession(
        connector=connector,
        skip_auto_headers=["User-Agent"],
        timeout=aiohttp.ClientTimeout(10),
    ) as session:
        try:
            original_url = url
            for _redirect in range(settings.MAXIMUM_REDIRECTS + 1):
                if not is_public_url(url):
                    logger.error(f"Refusing to download non-public URL: {url}")
                    return False

                async with session.get(url, allow_redirects=False) as response:
                    location = response.headers.get("Location")
                    if 300 <= response.status < 400 and location:
                        # TODO: Figure out which sites use 3xx as errors
                        if "imgur" in original_url:
                            logger.error(f"3xx response from {url}")
                            return False
                        logger.warning(f"3xx redirect from {url}")
                        url = str(response.url.join(URL(location)))
                        continue

                    if response.status == 200:
                        logger.info(f"200 response from {url}")
                        return await _save(response, url, path)

                    logger.error(f"{response.status} response from {url}")
                    return False

            logger.error(f"Too many redirects from {original_url}")

        except EXCEPTIONS as e:
            message = str(e).strip("() ") or e.__class__.__name__
            logger.error(f"5xx response from {url}: {message}")

    return False


async def _save(response: aiohttp.ClientResponse, url: str, path: AsyncPath) -> bool:
    limit = settings.MAXIMUM_DOWNLOAD_SIZE
    if (response.content_length or 0) > limit:
        logger.error(f"Image too large ({response.content_length} bytes): {url}")
        return False

    size = 0
    f = await aiofiles.open(path, mode="wb")  # type: ignore
    try:
        async for chunk in response.content.iter_chunked(64 * 1024):
            size += len(chunk)
            if size > limit:
                logger.error(f"Image too large (over {limit} bytes): {url}")
                break
            await f.write(chunk)
    finally:
        await f.close()

    if size > limit:
        await path.unlink(missing_ok=True)
        return False
    return True
