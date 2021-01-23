from pprint import pformat
from urllib.parse import unquote, urlparse

import aiohttp
from sanic.log import logger

from .. import settings


def get_watermark(request, watermark: str) -> tuple[str, bool]:
    updated = False

    if watermark == "none":
        referer = request.headers.get("referer")
        logger.debug(f"Referer: {referer}")
        if referer:
            domain = urlparse(referer).netloc
            if domain in settings.ALLOWED_WATERMARKS:
                return "", False
            return settings.DEFAULT_WATERMARK, True

        data = pformat(
            {
                name: getattr(request, name)
                for name in dir(request)
                if not name.startswith("_")
            }
        )
        logger.warning(f"Watermark removal request:\n{data}")
        return "", False

    if watermark:

        if watermark == settings.DEFAULT_WATERMARK:
            logger.warning(f"Redundant watermark: {watermark}")
            return watermark, True

        if watermark not in settings.ALLOWED_WATERMARKS:
            logger.warning(f"Unknown watermark: {watermark}")
            return settings.DEFAULT_WATERMARK, True

        return watermark, False

    return settings.DEFAULT_WATERMARK, False


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
