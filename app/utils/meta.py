from urllib.parse import unquote, urlparse

import aiohttp
from sanic.log import logger

from .. import settings


def get_watermark(request, watermark: str) -> tuple[str, bool]:
    updated = False

    if watermark == "none":
        logger.info(request.headers)
        referer = request.headers.get("referer")
        if referer:
            domain = urlparse(referer).netloc
            logger.info(f"{referer=} {domain=}")
            if domain in settings.ALLOWED_WATERMARKS:
                watermark = ""
            else:
                watermark = "bad request"
        else:
            watermark = "no referer"

    elif watermark:
        if watermark == settings.DEFAULT_WATERMARK:
            logger.warning(f"Redundant watermark: {watermark}")
            updated = True
        elif watermark not in settings.ALLOWED_WATERMARKS:
            logger.warning(f"Unknown watermark: {watermark}")
            watermark = settings.DEFAULT_WATERMARK
            updated = True

    else:
        watermark = settings.DEFAULT_WATERMARK

    return watermark, updated


async def track(request, lines: list[str]):
    text = " ".join(lines).strip()
    trackable = not any(
        name in request.args for name in ["height", "width", "watermark"]
    )
    if text and trackable and settings.REMOTE_TRACKING_URL:
        async with aiohttp.ClientSession() as session:
            params = dict(
                text=text,
                source="memegen.link",
                context=unquote(request.url),
            )
            logger.info(f"Tracking request: {params}")
            response = await session.get(settings.REMOTE_TRACKING_URL, params=params)
            if response.status != 200:
                try:
                    message = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    message = response.text
                logger.error(f"Tracker response: {message}")
