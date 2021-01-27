from urllib.parse import unquote, urlparse

import aiohttp
from sanic.log import logger

from .. import settings


def get_watermark(request, watermark: str) -> tuple[str, bool]:
    api_key = request.headers.get("x-api-key")
    if api_key:
        api_mask = api_key[:2] + "***" + api_key[-2:]
        logger.info(f"Authenticated with {api_mask}")
        if api_key in settings.API_KEYS:
            return "", False

    if watermark == settings.DISABLED_WATERMARK:
        referer = request.headers.get("referer") or request.args.get("referer")
        logger.info(f"Watermark removal referer: {referer}")
        if referer:
            domain = urlparse(referer).netloc
            if domain in settings.ALLOWED_WATERMARKS:
                return "", False

        return settings.DEFAULT_WATERMARK, True

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
