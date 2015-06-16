from flask import Blueprint, current_app as app, redirect, url_for, send_file

from .. import domain

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("<key>/<top>/<bottom>.<kind>")
def get_visible(key, top, bottom, kind):
    template = domain.Template(key)
    text = domain.Text(top, bottom)
    _path = app.image_service.create_image(template, text, kind)
    return send_file(_path, mimetype='image/jpeg')


@blueprint.route("<code>.<kind>")
def get_hidden(code, kind):
    key, top, bottom = app.link_service.decode(code)
    # TODO: maybe this shouldn't redirect
    # url = url_for('.get_visible', key=key, top=top, bottom=bottom, kind=kind)
    # return redirect(url)
    template = domain.Template(key)
    text = domain.Text(top, bottom)
    _path = app.image_service.create_image(template, text, kind)
    return send_file(_path, mimetype='image/jpeg')
