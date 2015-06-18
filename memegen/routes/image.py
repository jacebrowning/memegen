from flask import Blueprint, current_app as app, redirect, url_for, send_file

from .. import domain

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("<key>/<path:path>.jpg")
def get(key, path):
    template = app.template_service.find(key)
    text = domain.Text(path)
    if path != text.path:
        return redirect(url_for(".get", key=key, path=text.path))
    image = app.image_service.create_image(template, text)
    return send_file(image, mimetype='image/jpeg')


@blueprint.route("<code>.jpg")
def get_encoded(code):
    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create_image(template, text)
    return send_file(image, mimetype='image/jpeg')
