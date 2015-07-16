from flask import Blueprint, url_for, redirect, send_file
from flask import current_app as app, request
import requests

from .. import domain

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("<key>.jpg")
def get_without_text(key):
    template = app.template_service.find(key)
    text = domain.Text(template.default or '_')
    return redirect(url_for(".get", key=key, path=text.path))


@blueprint.route("<key>/<path:path>.jpg", endpoint='get')
def get_with_text(key, path):
    text = domain.Text(path)
    track_request(str(text))

    template = app.template_service.find(key)
    if template.key != key:
        return redirect(url_for(".get", key=template.key, path=path))

    if path != text.path:
        return redirect(url_for(".get", key=key, path=text.path))

    image = app.image_service.create_image(template, text)

    track_request(str(text))
    return send_file(image.path, mimetype='image/jpeg')


@blueprint.route("_<code>.jpg")
def get_encoded(code):
    track_request(code)

    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create_image(template, text)

    track_request(str(text))
    return send_file(image.path, mimetype='image/jpeg')


def track_request(title):
    data = dict(
        v=1,
        tid='UA-6468614-10',
        cid=request.remote_addr,

        t='pageview',
        dh='memegen.link',
        dp=request.path,
        dt=title,
    )
    if not app.config['TESTING']:  # pragma: no cover (manual)
        requests.post("http://www.google-analytics.com/collect", data=data)
