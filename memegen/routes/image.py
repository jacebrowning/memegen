import logging

from flask import Blueprint, current_app, request, redirect
from webargs import fields, flaskparser

from .. import domain

from ._cache import Cache
from ._utils import route, track, display


blueprint = Blueprint('image', __name__)
log = logging.getLogger(__name__)
cache_filtered = Cache()
cache_unfiltered = Cache(filtered=False)

OPTIONS = {
    'alt': fields.Str(missing=None),
    'font': fields.Str(missing=None),
    'preview': fields.Bool(missing=False),
    'share': fields.Bool(missing=False),
    'width': fields.Int(missing=None),
    'height': fields.Int(missing=None),
    'watermark': fields.Str(missing=None),
}


@blueprint.route("/latest.jpg")
@blueprint.route("/latest<int:index>.jpg")
@flaskparser.use_kwargs({'filtered': fields.Bool(missing=True)})
def get_latest(index=1, filtered=True):
    cache = cache_filtered if filtered else cache_unfiltered
    kwargs = cache.get(index - 1)

    if kwargs:
        kwargs['preview'] = True
    else:
        kwargs['key'] = 'custom'
        kwargs['path'] = "your_meme/goes_here"
        kwargs['alt'] = "https://raw.githubusercontent.com/jacebrowning/memegen/master/memegen/static/images/missing.png"

    return redirect(route('.get', _external=True, **kwargs))


@blueprint.route("/<key>.jpg")
@flaskparser.use_kwargs(OPTIONS)
def get_without_text(key, **options):
    options.pop('preview')
    options.pop('share')

    template = current_app.template_service.find(key)
    text = domain.Text(template.default_path)

    return redirect(route('.get', key=key, path=text.path, **options))


@blueprint.route("/<key>.jpeg")
def get_without_text_jpeg(key):
    return redirect(route('.get_without_text', key=key))


@blueprint.route("/<key>/<path:path>.jpg", endpoint='get')
@flaskparser.use_kwargs(OPTIONS)
def get_with_text(key, path, alt, font, watermark, preview, share, **size):
    options = dict(key=key, path=path,
                   alt=alt, font=font, watermark=watermark, **size)
    if preview:
        options['preview'] = True
    if share:
        options['share'] = True

    text = domain.Text(path)
    fontfile = current_app.font_service.find(font)

    template = current_app.template_service.find(key, allow_missing=True)
    if template.key != key:
        options['key'] = template.key
        return redirect(route('.get', **options))

    if alt and template.path == template.get_path(alt):
        options.pop('alt')
        return redirect(route('.get', **options))

    if path != text.path:
        options['path'] = text.path
        return redirect(route('.get', **options))

    if font and not fontfile:
        options.pop('font')
        return redirect(route('.get', **options))

    watermark, valid = _get_watermark(request, watermark)
    if not valid:
        options.pop('watermark')
        return redirect(route('.get', **options))

    image = current_app.image_service.create(
        template, text,
        style=alt, font=fontfile, size=size, watermark=watermark,
    )

    if not preview:
        cache_filtered.add(key=key, path=path, alt=alt, font=font)
        cache_unfiltered.add(key=key, path=path, alt=alt, font=font)
        track(image.text)

    return display(image.text, image.path, share=share)


@blueprint.route("/<key>/<path:path>.jpeg")
def get_with_text_jpeg(key, path):
    return redirect(route('.get', key=key, path=path))


@blueprint.route("/_<code>.jpg")
def get_encoded(code):

    key, path = current_app.link_service.decode(code)
    template = current_app.template_service.find(key)
    text = domain.Text(path)
    image = current_app.image_service.create(template, text)

    track(image.text)

    return display(image.text, image.path)


def _get_watermark(_request, watermark):
    referrer = _request.environ.get('HTTP_REFERER', "")
    agent = _request.environ.get('HTTP_USER_AGENT', "")
    log.debug("Referrer: %r, Agent: %r", referrer, agent)

    if watermark == 'none':
        for option in current_app.config['WATERMARK_OPTIONS']:
            for identity in (referrer, agent):
                if option in identity:
                    log.debug("Watermark disabled (%r in %r)", option, identity)
                    return None, True
        log.warning("Request does not support unmarked images")
        return None, False

    if watermark and watermark not in current_app.config['WATERMARK_OPTIONS']:
        log.warning("Unsupported custom watermark: %r", watermark)
        return watermark, False

    if watermark:
        log.debug("Using custom watermark: %r", watermark)
        return watermark, True

    default = current_app.config['WATERMARK_OPTIONS'][0]
    log.debug("Using default watermark: %r", default)
    return default, True
