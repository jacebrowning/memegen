from flask import Blueprint, current_app as app, redirect, url_for, send_file

from .. import domain

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("<key>.jpg")
def get_without_text(key):
    template = app.template_service.find(key)
    text = domain.Text(template.default or '_')
    return redirect(url_for(".get", key=key, path=text.path))


@blueprint.route("<key>/<path:path>.jpg", endpoint='get')
def get_with_text(key, path):
    template = app.template_service.find(key)
    text = domain.Text(path)
    if path != text.path:
        return redirect(url_for(".get", key=key, path=text.path))
    image = app.image_service.create_image(template, text)
    return send_file(image.path, mimetype='image/jpeg')


@blueprint.route("_<code>.jpg")
def get_encoded(code):
    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create_image(template, text)
    return send_file(image.path, mimetype='image/jpeg')
