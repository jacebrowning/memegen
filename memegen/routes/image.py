import logging

from flask import Blueprint, current_app as app, redirect
from webargs import fields, flaskparser

from .. import domain

from ._common import route, display

blueprint = Blueprint('image', __name__, url_prefix="/")
log = logging.getLogger(__name__)

OPTIONS = {
    'alt': fields.Str(missing=None)  # pylint: disable=no-member
}


@blueprint.route("latest.jpg")
def get_latest():
    title = "Latest Meme"
    try:
        image = app.image_service.image_store.latest
        if image.style:
            _route = route('.get', key=image.template.key, path=image.text.path,
                           alt=image.style)
        else:
            _route = route('.get', key=image.template.key, path=image.text.path)
        return redirect(_route, code=307)
    except FileNotFoundError:
        return display(title, "static/images/missing.png", mimetype='image/png')


@blueprint.route("<key>.jpg")
@flaskparser.use_kwargs(OPTIONS)
def get_without_text(key, alt):
    template = app.template_service.find(key)
    text = domain.Text(template.default_path)
    return redirect(route('.get', key=key, path=text.path, alt=alt))


@blueprint.route("<key>.jpeg")
def get_without_text_jpeg(key):
    return redirect(route('.get_without_text', key=key))


@blueprint.route("<key>/<path:path>.jpg", endpoint='get')
@flaskparser.use_kwargs(OPTIONS)
def get_with_text(key, path, alt):
    text = domain.Text(path)

    template = app.template_service.find(key, allow_missing=True)
    if template.key != key:
        return redirect(route('.get', key=template.key, path=path, alt=alt))

    if alt and template.path == template.get_path(alt):
        return redirect(route('.get', key=key, path=path))

    if path != text.path:
        return redirect(route('.get', key=key, path=text.path, alt=alt))

    image = app.image_service.create_image(template, text, style=alt)

    return display(image.text, image.path)


@blueprint.route("<key>/<path:path>.jpeg")
def get_with_text_jpeg(key, path):
    return redirect(route('.get', key=key, path=path))


@blueprint.route("_<code>.jpg")
def get_encoded(code):

    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create_image(template, text)

    return display(image.text, image.path)
