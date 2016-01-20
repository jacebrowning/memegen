import logging
from urllib.parse import unquote

import requests
from flask import url_for as _url_for


GITHUB_BASE = "https://raw.githubusercontent.com/jacebrowning/memegen/master/"
CONTRIBUTING_URL = GITHUB_BASE + "CONTRIBUTING.md"
CHANGES_URL = GITHUB_BASE + "CHANGES.md"

log = logging.getLogger(__name__)


def url_for(*args, **kwargs):
    """Unquoted version of Flask's `url_for`."""
    return unquote(_url_for(*args, **kwargs))


def samples(app):
    """Generate dictionaries of sample image data for template rendering."""
    for template in sorted(app.template_service.all()):
        path = template.sample_path
        url = url_for('image.get', key=template.key, path=path, _external=True)
        link = url_for('links.get', key=template.key, path=path)
        yield {
            'key': template.key,
            'name': template.name,
            'url': url,
            'link': link
        }


def track(app, request, title):
    """Log the requested content."""
    data = dict(
        v=1,
        tid=app.config['GOOGLE_ANALYTICS_TID'],
        cid=request.remote_addr,

        t='pageview',
        dh='memegen.link',
        dp=request.path,
        dt=str(title),

        uip=request.remote_addr,
        ua=request.user_agent.string,
        dr=request.referrer,
    )
    if app.config['DEBUG']:
        for key in sorted(data):
            log.debug("%s=%r", key, data[key])
    else:
        requests.post("http://www.google-analytics.com/collect", data=data)
