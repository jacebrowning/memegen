import logging

from flask import Blueprint, current_app as app, redirect
from webargs import fields, flaskparser

from .. import domain

from ._cache import Cache
from ._utils import route, track, display


blueprint = Blueprint('image', __name__)
log = logging.getLogger(__name__)
cache = Cache()

OPTIONS = {
    'alt': fields.Str(missing=None),
    'font': fields.Str(missing=None),
    'preview': fields.Bool(missing=False),
    'share': fields.Bool(missing=False)
}


@blueprint.route("/latest.jpg")
@blueprint.route("/latest<int:index>.jpg")
def get_latest(index=1):
    kwargs = cache.get(index - 1)

    if not kwargs:
        kwargs['key'] = 'custom'
        kwargs['path'] = "your-meme/goes-here"
        kwargs['alt'] = "https://raw.githubusercontent.com/jacebrowning/memegen/master/memegen/static/images/missing.png"

    return redirect(route('.get', _external=True, **kwargs))


@blueprint.route("/<key>.jpg")
@flaskparser.use_kwargs(OPTIONS)
def get_without_text(key, **options):
    options.pop('preview')
    options.pop('share')

    template = app.template_service.find(key)
    text = domain.Text(template.default_path)

    return redirect(route('.get', key=key, path=text.path, **options))


@blueprint.route("/<key>.jpeg")
def get_without_text_jpeg(key):
    return redirect(route('.get_without_text', key=key))


@blueprint.route("/<key>/<path:path>.jpg", endpoint='get')
@flaskparser.use_kwargs(OPTIONS)
def get_with_text(key, path, alt, font, preview, share):
    options = dict(key=key, path=path, alt=alt, font=font)
    if preview:
        options['preview'] = 'true'

    if share:
        options['share'] = 'true'

    text = domain.Text(path)
    fontfile = app.font_service.find(font)

    template = app.template_service.find(key, allow_missing=True)
    if template.key != key:
        options['key'] = template.key
        return redirect(route('.get', **options))

    if alt and template.path == template.get_path(alt):
        options.pop('alt')
        return redirect(route('.get', **options))

    if font and not fontfile:
        options.pop('font')
        return redirect(route('.get', **options))

    if path != text.path:
        options['path'] = text.path
        return redirect(route('.get', **options))

    image = app.image_service.create(template, text, style=alt, font=fontfile)

    if not preview:
        cache.add(key=key, path=path, style=alt, font=font)
        track(image.text)

    return display(image.text, image.path, share=share)


@blueprint.route("/<key>/<path:path>.jpeg")
def get_with_text_jpeg(key, path):
    return redirect(route('.get', key=key, path=path))


@blueprint.route("/_<code>.jpg")
def get_encoded(code):

    key, path = app.link_service.decode(code)
    template = app.template_service.find(key)
    text = domain.Text(path)
    image = app.image_service.create(template, text)

    track(image.text)

    return display(image.text, image.path)
