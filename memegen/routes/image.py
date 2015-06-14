from flask import Blueprint, current_app as app, send_file

from .. import domain

blueprint = Blueprint('image', __name__, url_prefix="/")


@blueprint.route("<key>/<top>/<bottom>.<kind>")
def get(key, top, bottom, kind):
    template = domain.Template(key)
    text = domain.Text(top, bottom)
    _path = app.image_service.create_image(template, text, kind)
    return send_file(_path, mimetype='image/png')
