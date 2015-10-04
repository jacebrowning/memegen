from flask import Blueprint, redirect, send_file
from flask import current_app as app, request
import requests

from .. import domain

from ._common import url_for

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("latest.jpg")
def get_latest():
    path = app.image_service.image_store.latest
    try:
        return send_file(path, mimetype='image/jpeg')
    except FileNotFoundError:
        # TODO: return our logo when one exists?
        return get_without_text("fry")


@blueprint.route("<key>.jpg")
def get_without_text(key):
    template = app.template_service.find(key)
    text = domain.Text(template.default_path or '_')
    return redirect(url_for(".get", key=key, path=text.path))


@blueprint.route("<key>.jpeg")
def get_without_text_jpeg(key):
    return redirect(url_for(".get_without_text", key=key))


@blueprint.route("<key>/<path:path>.jpg", endpoint='get')
def get_with_text(key, path):
    text = domain.Text(path)
    track_request(text)

    template = app.template_service.find(key)
    if template.key != key:
        return redirect(url_for(".get", key=template.key, path=path))

    if path != text.path:
        return redirect(url_for(".get", key=key, path=text.path))

    image = app.image_service.create_image(template, text)

    track_request(text)
    return send_file(image.path, mimetype='image/jpeg')


@blueprint.route("<key>/<path:path>.jpeg")
def get_with_text_jpeg(key, path):
    return redirect(url_for(".get", key=key, path=path))


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
