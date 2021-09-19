from pathlib import Path
from urllib.parse import unquote

import aiohttp
import bugsnag
from aiocache import cached
from sanic.log import logger

from .. import settings


def version() -> str:
    changelog_lines = Path("CHANGELOG.md").read_text().splitlines()
    version_heading = changelog_lines[2]
    return version_heading.split(" ")[-1]


@cached(ttl=60 * 15 if settings.DEPLOYED else 0)
async def authenticate(request) -> dict:
    info: dict = {}
    if settings.REMOTE_TRACKING_URL:
        api = settings.REMOTE_TRACKING_URL + "auth"
    else:
        return info

    api_key = _get_api_key(request)
    if api_key:
        api_mask = api_key[:2] + "***" + api_key[-2:]
        logger.info(f"Authenticating with API key: {api_mask}")
        async with aiohttp.ClientSession() as session:
            response = await session.get(api, headers={"X-API-KEY": api_key})
            info = await response.json()

    return info


@cached(ttl=60 * 15 if settings.DEPLOYED else 0)
async def tokenize(request, url: str) -> tuple[str, bool]:
    api_key = _get_api_key(request) or ""
    token = request.args.get("token")
    default_url = url.replace(f"api_key={api_key}", "").replace("?&", "?").strip("?&")

    if api_key == "myapikey42" and "example.png" not in url:
        logger.warning(f"Example API key used to tokenize: {url}")
        return default_url, True

    if settings.REMOTE_TRACKING_URL:
        api = settings.REMOTE_TRACKING_URL + "tokenize"
    else:
        return url, False

    if api_key or token:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                api, data={"url": default_url}, headers={"X-API-KEY": api_key}
            )
            data = await response.json()
            return data["url"], data["url"] != url

    return url, False


async def custom_watermarks_allowed(request) -> bool:
    info = await authenticate(request)
    if info.get("image_access", False):
        return True

    token = request.args.get("token")
    if token:
        logger.info(f"Authenticating with token: {token}")
        _url, updated = await tokenize(request, request.url)
        return not updated

    return False


async def get_watermark(request) -> tuple[str, bool]:
    watermark = request.args.get("watermark", "")

    if await custom_watermarks_allowed(request):
        if watermark == settings.DISABLED_WATERMARK:
            return "", False
        return watermark, False

    if watermark:
        if watermark == settings.DEFAULT_WATERMARK:
            logger.warning(f"Redundant watermark: {watermark}")
            return settings.DEFAULT_WATERMARK, True
        if watermark in settings.ALLOWED_WATERMARKS:
            return watermark, False
        logger.warning(f"Invalid watermark: {watermark}")
        return settings.DEFAULT_WATERMARK, True

    return settings.DEFAULT_WATERMARK, False


async def track(request, lines: list[str]):
    if settings.TRACK_REQUESTS and settings.REMOTE_TRACKING_URL:
        api = settings.REMOTE_TRACKING_URL
    else:
        return

    text = " ".join(lines).strip()
    if not text:
        return
    if any(name in request.args for name in ["height", "width", "watermark"]):
        return
    if settings.DEPLOYED and "localhost" in request.host:
        return

    async with aiohttp.ClientSession() as session:
        params = dict(
            text=text,
            client=_get_referer(request) or settings.BASE_URL,
            result=unquote(request.url),
        )
        logger.info(f"Tracking request: {params}")
        headers = {"X-API-KEY": _get_api_key(request) or ""}
        response = await session.get(api, params=params, headers=headers)
        if response.status != 200:
            try:
                message = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                message = await response.text()
            logger.error(f"Tracker response {response.status}: {message}")
        if response.status >= 404 and response.status not in {414, 421, 520}:
            settings.REMOTE_TRACKING_ERRORS += 1
            logger.info(f"Tracker error count: {settings.REMOTE_TRACKING_ERRORS}")
            if settings.REMOTE_TRACKING_ERRORS >= settings.REMOTE_TRACKING_ERRORS_LIMIT:
                settings.TRACK_REQUESTS = False
                bugsnag.notify(
                    RuntimeError(f"Disabled tracking after {response.status} response"),
                    metadata={"request": request.url, "message": message},
                )


async def search(request, text: str, safe: bool, *, mode="") -> list[dict]:
    if settings.REMOTE_TRACKING_URL:
        api = settings.REMOTE_TRACKING_URL + mode
    else:
        return []

    async with aiohttp.ClientSession() as session:
        params = dict(
            text=text,
            nsfw=0 if safe else 1,
            client=_get_referer(request) or settings.BASE_URL,
        )
        logger.info(f"Searching for results: {text!r} (safe={safe})")
        headers = {"X-API-KEY": _get_api_key(request) or ""}
        response = await session.get(api, params=params, headers=headers)
        assert response.status < 500, f"Invalid response: {response}"

        data = await response.json()
        if response.status == 200:
            return data

        logger.error(f"Search response: {data}")
        return []


def _get_referer(request):
    referer = request.headers.get("referer") or request.args.get("referer")
    if referer and referer.startswith(settings.BASE_URL) and "/docs/" not in referer:
        referer = None
    return referer


def _get_api_key(request):
    return request.headers.get("x-api-key") or request.args.get("api_key")
