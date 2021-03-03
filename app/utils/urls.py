from urllib.parse import parse_qs, urlencode, urlparse

from .. import settings
from .meta import _get_api_key


def normalize(request, url: str) -> str:
    parts = urlparse(url)
    url = f"{settings.BASE_URL}{parts.path}"
    if "background" in parts.query:
        background = parse_qs(parts.query)["background"][0]
    else:
        background = ""
    query = params(request, background=background)
    if query:
        url += "?" + urlencode(query)
    return clean(url)


def params(request, **kwargs) -> dict:
    kwargs["api_key"] = _get_api_key(request)
    return {k: v for k, v in kwargs.items() if v}


def clean(url: str) -> str:
    url = _unquote_slashes(url)
    url = _drop_trailing_spaces(url)
    return url


def _unquote_slashes(url: str) -> str:
    return url.replace("%3A%2F%2F", "://").replace("%2F", "/")


def _drop_trailing_spaces(url: str) -> str:
    while "/_." in url:
        url = url.replace("/_.", ".")
    return url
