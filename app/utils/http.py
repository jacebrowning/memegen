import asyncio

import aiofiles
import aiohttp
import aiohttp.client_exceptions
from aiopath import AsyncPath
from sanic.log import logger

EXCEPTIONS = (
    aiohttp.client_exceptions.ClientConnectionError,
    aiohttp.client_exceptions.InvalidURL,
    aiohttp.client_exceptions.TooManyRedirects,
    AssertionError,
    asyncio.TimeoutError,
    UnicodeError,
)


async def fetch(url: str, **kwargs) -> tuple[int, dict | str]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10, **kwargs) as response:

                try:
                    message = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    message = await response.text()

                return response.status, message

        except EXCEPTIONS as e:
            message = str(e).strip("() ") or e.__class__.__name__

            return 500, message


async def download(url: str, path: AsyncPath) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:

                if response.history:
                    logger.error(f"3xx response from {url}")
                    return False

                if response.status == 200:
                    logger.info(f"200 response from {url}")
                    f = await aiofiles.open(path, mode="wb")  # type: ignore
                    await f.write(await response.read())
                    await f.close()
                    return True

                logger.error(f"{response.status} response from {url}")

        except EXCEPTIONS as e:
            message = str(e).strip("() ") or e.__class__.__name__
            logger.error(f"5xx response from {url}: {message}")

    return False
