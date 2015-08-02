from urllib.parse import unquote

from flask import url_for as _url_for


GITHUB_BASE = "http://github.com/jacebrowning/memegen/"
CONTRIBUTING = GITHUB_BASE + "blob/master/CONTRIBUTING.md"


def url_for(*args, **kwargs):
    """Unquoted version of Flask's `url_for`."""
    return unquote(_url_for(*args, **kwargs))
