from urllib.parse import unquote

from flask import current_app as app
from flask import url_for as _url_for


GITHUB_BASE = "http://github.com/jacebrowning/memegen/"
CONTRIBUTING = GITHUB_BASE + "blob/master/CONTRIBUTING.md"


def url_for(*args, **kwargs):
    """Unquoted version of Flask's `url_for`."""
    return unquote(_url_for(*args, **kwargs))


def samples():
    """Generate dictionaries of sample image data for template rendering."""
    for template in sorted(app.template_service.all()):
        path = template.sample_path
        url = url_for("image.get", key=template.key, path=path, _external=True)
        link = url_for("links.get", key=template.key, path=path)
        yield {
            'key': template.key,
            'name': template.name,
            'url': url,
            'link': link
        }
