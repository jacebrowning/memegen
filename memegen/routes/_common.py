import pprint
import logging
from urllib.parse import unquote

import requests
from flask import (Response, url_for, render_template, send_file,
                   current_app, request)

GITHUB_SLUG = "jacebrowning/memegen"
GITHUB_BASE = "https://raw.githubusercontent.com/{}/master/".format(GITHUB_SLUG)
CONTRIBUTING_URL = GITHUB_BASE + "CONTRIBUTING.md"
CHANGES_URL = GITHUB_BASE + "CHANGELOG.md"

log = logging.getLogger(__name__)


def route(*args, **kwargs):
    """Unquoted version of Flask's `url_for`."""
    return _secure(unquote(url_for(*args, **kwargs)))


def samples(blank=False):
    """Generate dictionaries of sample image data for template rendering."""
    for template in sorted(current_app.template_service.all()):
        path = "_" if blank else template.sample_path
        url = route('image.get', key=template.key, path=path)
        yield {
            'key': template.key,
            'name': template.name,
            'url': url,
        }


def display(title, path, raw=False, mimetype='image/jpeg'):
    """Render a webpage or raw image based on request."""
    mimetypes = request.headers.get('Accept', "").split(',')
    browser = 'text/html' in mimetypes

    if browser:
        log.info("Rending image on page: %s", request.url)

        html = render_template(
            'image.html',
            src=_secure(request.url),
            title=title,
            ga_tid=get_tid(),
        )
        return html if raw else Response(html)

    else:
        log.info("Sending image: %s", path)
        _track(title)
        return send_file(path, mimetype=mimetype)


def _secure(url):
    """Ensure HTTPS is used in production."""
    if current_app.config['ENV'] == 'prod':
        url = url.replace('http:', 'https:')
    return url


def _track(title):
    """Log the requested content, server-side."""
    data = dict(
        v=1,
        tid=get_tid(),
        cid=request.remote_addr,

        t='event',
        ec='Image',
        ea='GET',
        el=str(title),

        uip=request.remote_addr,
        ua=request.user_agent.string,
        dr=request.referrer,
    )
    if get_tid(default=None):
        requests.post("http://www.google-analytics.com/collect", data=data)
    else:
        log.debug("Analytics data:\n%s", pprint.pformat(data))


def get_tid(*, default='local'):
    """Get the analtyics tracking identifier."""
    return current_app.config['GOOGLE_ANALYTICS_TID'] or default
