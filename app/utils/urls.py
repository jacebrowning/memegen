from urllib.parse import unquote, urlencode

from furl import furl

from .. import settings

FLAGS = {
    "0": False,
    "1": True,
    "false": False,
    "no": False,
    "true": True,
    "yes": True,
}


def self(url: furl) -> bool:
    return url.netloc and ("memegen.link" in url.netloc or "localhost" in url.netloc)


def schema(value) -> bool:
    return value and "://" in value


def arg(data: dict, default, *names: str):
    for name in names:
        value = data.get(name)
        if value is not None:
            return value
    return default


def flag(request, name, default=None):
    value = request.args.get(name, "").lower()
    return FLAGS.get(value, default)


def add(url: str, **kwargs):
    joiner = "&" if "?" in url else "?"
    return url + joiner + urlencode(kwargs)


def normalize(url: str) -> str:
    original = furl(url)
    normalized = furl(f"{settings.BASE_URL}{original.path}")

    if "background" in original.args:
        normalized.args["background"] = original.args["background"]

    return clean(str(normalized))


def params(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v}


def clean(url: str) -> str:
    # Replace percent-encoded characters
    if "background=" in url:
        url = url.replace("%3A", ":").replace("%2F", "/")
    else:
        url = unquote(url)

    # Replace invalid regex escape sequences
    url = url.replace("\\", "~b")
    url = url.replace("\n", "~n")

    # Replace spaces with underscores
    url = url.replace(" ", "_")

    # Drop trailing spaces
    while "/_." in url:
        url = url.replace("/_.", ".")

    # TODO: Fix Sanic bug?
    # https://github.com/jacebrowning/memegen/issues/799
    url = url.replace("::", ":")

    return url
