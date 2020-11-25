from urllib.parse import unquote

import aiohttp
from sanic.log import logger

from .. import settings


def get_watermark(request, watermark: str) -> str:
    if watermark == "none":
        watermark = ""
    elif watermark:
        if watermark not in settings.ALLOWED_WATERMARKS:
            logger.warning(f"Unknown watermark: {watermark}")
    else:
        watermark = settings.DEFAULT_WATERMARK
    return watermark


async def track_url(request, lines):
    if settings.REMOTE_TRACKING_URL:  # pragma: no cover
        async with aiohttp.ClientSession() as session:
            params = dict(
                text=" ".join(lines),
                source="memegen.link",
                context=unquote(request.url),
            )
            response = await session.get(settings.REMOTE_TRACKING_URL, params=params)
            if response.status != 200:
                try:
                    message = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    message = response.text
                logger.error(f"Tracker response: {message}")
