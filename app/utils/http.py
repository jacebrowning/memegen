import aiofiles
import aiohttp
import aiohttp.client_exceptions
from aiopath import AsyncPath
from sanic.log import logger

_EXCEPTIONS = (
    aiohttp.client_exceptions.ClientConnectionError,
    aiohttp.client_exceptions.InvalidURL,
    aiohttp.client_exceptions.TooManyRedirects,
    AssertionError,
    UnicodeError,
)


async def download(url: str, path: AsyncPath) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:

                if response.status == 200:
                    f = await aiofiles.open(path, mode="wb")  # type: ignore
                    await f.write(await response.read())
                    await f.close()
                    return True

                logger.error(f"{response.status} response from {url}")

        except _EXCEPTIONS as e:
            message = str(e).strip("() ")
            logger.error(f"Invalid response from {url}: {message}")

    return False
