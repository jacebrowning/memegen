import aiofiles
import aiohttp
from aiohttp.client_exceptions import ClientConnectionError, InvalidURL
from aiopath import AsyncPath
from sanic.log import logger


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

        except (InvalidURL, ClientConnectionError, AssertionError) as e:
            message = str(e).strip("() ")
            logger.error(f"Invalid response from {url}: {message}")

    return False
