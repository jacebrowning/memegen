from flask import Blueprint, current_app as app, redirect, url_for, send_file

from .. import domain

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("<key>/<path:path>.jpg")
def get(key, path):
    template = domain.Template(key)
    text = domain.Text(path)
    if path != text.path:
        return redirect(url_for(".get", key=key, path=text.path))
    _path = app.image_service.create_image(template, text)
    return send_file(_path, mimetype='image/jpeg')


@blueprint.route("<code>.jpg")
def get_encoded(code):
    key, path = app.link_service.decode(code)
    # TODO: maybe this shouldn't redirect
    # url = url_for('.get_visible', key=key, top=top, bottom=bottom, kind=kind)
    # return redirect(url)
    template = domain.Template(key)
    text = domain.Text(path)
    _path = app.image_service.create_image(template, text)
    return send_file(_path, mimetype='image/jpeg')
