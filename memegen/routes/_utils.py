import pprint
import logging
from urllib.parse import unquote

import requests
from flask import (Response, url_for, render_template, send_file,
                   current_app, request)


log = logging.getLogger(__name__)


def route(*args, **kwargs):
    """Unquoted version of Flask's `url_for`."""
    return _secure(unquote(url_for(*args, **kwargs)))


def _secure(url):
    """Ensure HTTPS is used in production."""
    if current_app.config['ENV'] == 'prod':
        url = url.replace('http:', 'https:')
    return url


def display(title, path, share=False, raw=False, mimetype='image/jpeg'):
    """Render a webpage or raw image based on request."""
    mimetypes = request.headers.get('Accept', "").split(',')
    browser = 'text/html' in mimetypes
    src_url, href_url = _sanitize_url_params(request)

    if browser or share:
        log.info("Rending image on page: %s", src_url)

        html = render_template(
            'image.html',
            title=title,
            src=_secure(src_url),
            href=_secure(href_url),
            ga_tid=get_tid(),
        )
        return html if raw else _nocache(Response(html))

    else:
        log.info("Sending image: %s", path)
        return send_file(path, mimetype=mimetype)


def _sanitize_url_params(req):
    """Format query sting for rendering and links."""
    params = dict(req.args)

    src_params = {k: v[0] for k, v in params.items()
                  if k != 'share'}
    src_url = _add_params(req.base_url, **src_params)

    href_params = {k: v[0] for k, v in params.items()
                   if k not in ['width', 'height']}
    href_url = _add_params(req.base_url, **href_params)

    return src_url, href_url


def _add_params(base, **params):
    formatted_params = ["{}={}".format(k, v) for k, v in params.items()]
    if formatted_params:
        return base + "?{}".format("&".join(formatted_params))
    else:
        return base


def _nocache(response):
    """Ensure a response is not cached."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def track(title):
    """Log the requested content, server-side."""
    data = dict(
        v=1,
        tid=get_tid(),
        cid=request.remote_addr,

        t='pageview',
        dh='memegen.link',
        dp=request.full_path,
        dt=str(title),

        uip=request.remote_addr,
        ua=request.user_agent.string,
    )
    if get_tid(default=None):
        requests.post("http://www.google-analytics.com/collect", data=data)
    else:
        log.debug("Analytics data:\n%s", pprint.pformat(data))


def get_tid(*, default='local'):
    """Get the analtyics tracking identifier."""
    return current_app.config['GOOGLE_ANALYTICS_TID'] or default
