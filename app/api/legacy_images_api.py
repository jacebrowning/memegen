from sanic import Blueprint

from .images_api import render_image

blueprint = Blueprint("legacy-images", url_prefix="/")


@blueprint.get("/<key>.jpg")
async def blank(request, key):
    return await render_image(request, key, "")


@blueprint.get("/<key>/<lines:path>.jpg")
async def text(request, key, lines):
    return await render_image(request, key, lines)
