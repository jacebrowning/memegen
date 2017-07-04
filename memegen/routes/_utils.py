import logging
from urllib.parse import unquote

import requests
from flask import (Response, url_for, render_template, send_file,
                   current_app, request)


log = logging.getLogger(__name__)


def route(*args, **kwargs):
    """Unquoted version of Flask's `url_for`."""
    for key, value in sorted(kwargs.items()):
        if value is True:
            kwargs[key] = 'true'

    return _secure(unquote(url_for(*args, **kwargs)))


def display(title, path, share=False, raw=False, mimetype='image/jpeg'):
    """Render a webpage or raw image based on request."""
    img = _format_url(request, 'share')
    img_twitter = _format_url(
        request, 'share',
        width=current_app.config['TWITTER_IMAGE_WIDTH'],
        height=current_app.config['TWITTER_IMAGE_HEIGHT'],
    )
    img_facebook = _format_url(
        request, 'share',
        width=current_app.config['FACEBOOK_IMAGE_WIDTH'],
        height=current_app.config['FACEBOOK_IMAGE_HEIGHT'],
    )
    url = _format_url(request, 'width', 'height')

    if share:
        log.info("Sharing image on page: %s", img)

        html = render_template(
            'share.html',
            title=title,
            img=_secure(img),
            img_twitter=_secure(img_twitter),
            img_facebook=_secure(img_facebook),
            url=_secure(url),
            config=current_app.config,
        )
        return html if raw else _nocache(Response(html))

    else:
        log.info("Sending image: %s", path)
        return send_file(path, mimetype=mimetype)


def track(title):
    """Log the requested content, server-side."""
    google_url = current_app.config['GOOGLE_ANALYTICS_URL']
    google_tid = current_app.config['GOOGLE_ANALYTICS_TID']
    google_data = dict(
        v=1,
        tid=google_tid,
        cid=request.remote_addr,

        t='pageview',
        dh='memegen.link',
        dp=request.full_path,
        dt=str(title),

        uip=request.remote_addr,
        ua=request.user_agent.string,
    )
    if google_tid != 'localhost':
        response = requests.post(google_url, data=google_data)
        params = _format_query(google_data, as_string=True)
        log.debug("Tracking POST: %s %s", response.url, params)

    remote_url = current_app.config['REMOTE_TRACKING_URL']
    remote_data = dict(
        text=str(title),
        source='memegen.link',
        context=unquote(request.url),
    )
    if remote_url:
        response = requests.get(remote_url, params=remote_data)
        log.debug("Tracking GET: %s", response.url)


def _secure(url):
    """Ensure HTTPS is used in production."""
    if current_app.config['ENV'] == 'prod':
        if url.startswith('http:'):
            url = url.replace('http:', 'https:', 1)
    return url


def _format_url(req, *skip, **add):
    """Get a formatted URL with sanitized query parameters."""
    base = req.base_url

    options = {k: v[0] for k, v in dict(req.args).items() if k not in skip}
    options.update(add)

    params = _format_query(options)

    if params:
        return base + "?{}".format("&".join(params))
    else:
        return base


def _format_query(options, *, as_string=False):
    pattern = "{}={!r}" if as_string else "{}={}"
    pairs = sorted(pattern.format(k, v) for k, v in options.items())
    if as_string:
        return ' '.join(pairs)
    return pairs


def _nocache(response):
    """Ensure a response is not cached."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
