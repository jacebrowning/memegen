import logging

from flask import Blueprint, current_app as app, redirect
from webargs import fields, flaskparser

from .. import domain

from ._common import route, display
from ._cache import Cache


blueprint = Blueprint('image', __name__, url_prefix="/")
log = logging.getLogger(__name__)
cache = Cache()

OPTIONS = {
    'alt': fields.Str(missing=None),  # pylint: disable=no-member
    'font': fields.Str(missing=None),  # pylint: disable=no-member
}


@blueprint.route("latest.jpg")
def get_latest():
    kwargs = cache.get(0)

    if not kwargs:
        kwargs['key'] = 'custom'
        kwargs['path'] = "welcome-to/memegen.link"
        kwargs['alt'] = "https://raw.githubusercontent.com/jacebrowning/memegen/master/memegen/static/images/missing.png"

    return redirect(route('.get', _external=True, **kwargs))


@blueprint.route("<key>.jpg")
@flaskparser.use_kwargs(OPTIONS)
def get_without_text(key, **kwargs):
    template = app.template_service.find(key)
    text = domain.Text(template.default_path)
    return redirect(route('.get', key=key, path=text.path, **kwargs))


@blueprint.route("<key>.jpeg")
def get_without_text_jpeg(key):
    return redirect(route('.get_without_text', key=key))


@blueprint.route("<key>/<path:path>.jpg", endpoint='get')
@flaskparser.use_kwargs(OPTIONS)
def get_with_text(key, path, alt, font):
    text = domain.Text(path)
    fontfile = app.font_service.find(font)

    template = app.template_service.find(key, allow_missing=True)
    if template.key != key:
        return redirect(route('.get', key=template.key, path=path, alt=alt))

    if alt and template.path == template.get_path(alt):
        return redirect(route('.get', key=key, path=path, font=font))

    if font and not fontfile:
        return redirect(route('.get', key=key, path=path, alt=alt))

    if path != text.path:
        return redirect(route(
            '.get', key=key, path=text.path, alt=alt, font=font))

    image = app.image_service.create(template, text, style=alt, font=fontfile)

    cache.add(key=key, path=path, style=alt, font=font)

    return display(image.text, image.path)


@blueprint.route("<key>/<path:path>.jpeg")
def get_with_text_jpeg(key, path):
    return redirect(route('.get', key=key, path=path))


@blueprint.route("_<code>.jpg")
def get_encoded(code):

    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create(template, text)

    return display(image.text, image.path)
