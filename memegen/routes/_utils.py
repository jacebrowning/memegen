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


def display(title, path, share=False, raw=False, mimetype='image/jpeg'):
    """Render a webpage or raw image based on request."""
    mimetypes = request.headers.get('Accept', "").split(',')
    browser = 'text/html' in mimetypes

    src = _format(request, 'share')
    src_twitter = _format(request, 'share',
                          width=current_app.config['TWITTER_IMAGE_WIDTH'],
                          height=current_app.config['TWITTER_IMAGE_HEIGHT'])
    src_facebook = _format(request, 'share',
                           width=current_app.config['FACEBOOK_IMAGE_WIDTH'],
                           height=current_app.config['FACEBOOK_IMAGE_HEIGHT'])
    href = _format(request, 'width', 'height')

    if share:
        log.info("Sharing image on page: %s", src)

        html = render_template(
            'share.html',
            title=title,
            src=_secure(src),
            src_twitter=_secure(src_twitter),
            src_facebook=_secure(src_facebook),
            href=_secure(href),
            config=current_app.config,
        )
        return html if raw else _nocache(Response(html))

    elif browser:
        log.info("Embedding image on page: %s", src)

        html = render_template(
            'image.html',
            title=title,
            src=_secure(src),
            config=current_app.config,
        )
        return html if raw else _nocache(Response(html))

    else:
        log.info("Sending image: %s", path)
        return send_file(path, mimetype=mimetype)


def track(title):
    """Log the requested content, server-side."""
    tid = current_app.config['GOOGLE_ANALYTICS_TID']

    data = dict(
        v=1,
        tid=tid,
        cid=request.remote_addr,

        t='pageview',
        dh='memegen.link',
        dp=request.full_path,
        dt=str(title),

        uip=request.remote_addr,
        ua=request.user_agent.string,
    )

    if tid == 'localhost':
        log.debug("Analytics data:\n%s", pprint.pformat(data))
    else:
        requests.post("http://www.google-analytics.com/collect", data=data)


def _secure(url):
    """Ensure HTTPS is used in production."""
    if current_app.config['ENV'] == 'prod':
        if url.startswith('http:'):
            url = url.replace('http:', 'https:', 1)
    return url


def _format(req, *skip, **add):
    """Get a formatted URL with sanitized query parameters."""
    base = req.base_url

    options = {k: v[0] for k, v in dict(req.args).items() if k not in skip}
    options.update(add)

    params = sorted("{}={}".format(k, v) for k, v in options.items())

    if params:
        return base + "?{}".format("&".join(params))
    else:
        return base


def _nocache(response):
    """Ensure a response is not cached."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
