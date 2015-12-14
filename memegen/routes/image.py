from flask import Blueprint, redirect, send_file
from flask import current_app as app, request
from webargs import flaskparser
import requests

from .. import domain

from ._common import OPTIONS, url_for

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("latest.jpg")
def get_latest():
    path = app.image_service.image_store.latest
    try:
        return send_file(path, mimetype='image/jpeg')
    except FileNotFoundError:
        return send_file("static/images/apple-touch-icon.png",
                         mimetype='image/png')


@blueprint.route("<key>.jpg")
@flaskparser.use_kwargs(OPTIONS)
def get_without_text(key, alt):
    template = app.template_service.find(key)
    text = domain.Text(template.default_path)
    return redirect(url_for('.get', key=key, path=text.path, alt=alt))


@blueprint.route("<key>.jpeg")
def get_without_text_jpeg(key):
    return redirect(url_for('.get_without_text', key=key))


@blueprint.route("<key>/<path:path>.jpg", endpoint='get')
@flaskparser.use_kwargs(OPTIONS)
def get_with_text(key, path, alt):
    text = domain.Text(path)
    track_request(text)

    template = app.template_service.find(key)
    if template.key != key:
        return redirect(url_for('.get', key=template.key, path=path, alt=alt))

    if alt and template.path == template.get_path(alt):
        return redirect(url_for('.get', key=key, path=path))

    if path != text.path:
        return redirect(url_for('.get', key=key, path=text.path, alt=alt))

    image = app.image_service.create_image(template, text, style=alt)

    track_request(text)
    return send_file(image.path, mimetype='image/jpeg')


@blueprint.route("<key>/<path:path>.jpeg")
def get_with_text_jpeg(key, path):
    return redirect(url_for('.get', key=key, path=path))


@blueprint.route("_<code>.jpg")
def get_encoded(code):
    track_request(code)

    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create_image(template, text)

    track_request(text)
    return send_file(image.path, mimetype='image/jpeg')


def track_request(title):
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
    if not app.config['TESTING']:  # pragma: no cover (manual)
        requests.post("http://www.google-analytics.com/collect", data=data)
