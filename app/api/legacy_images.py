from sanic import Blueprint

from .images import render_image

blueprint = Blueprint("legacy-images", url_prefix="/")


@blueprint.get("/<key>.png")
async def blank(request, key):
    return await render_image(key)


@blueprint.get("/<key>.jpg")
async def blank_jpg(request, key):
    return await render_image(key, ext="jpg")


@blueprint.get("/<key>/<slug:path>.png")
async def text(request, key, slug):
    return await render_image(key, slug)


@blueprint.get("/<key>/<slug:path>.jpg")
async def text_jpg(request, key, slug):
    return await render_image(key, slug, ext="jpg")
