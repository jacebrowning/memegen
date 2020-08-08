import asyncio

from sanic import Blueprint, response
from sanic.log import logger
from sanic_openapi import doc

from .. import helpers, models, settings, utils
from ..helpers import save_image

blueprint = Blueprint("images", url_prefix="/api/images")


@blueprint.get("/")
async def index(request):
    urls = helpers.get_sample_images(request)
    return response.json([{"url": url} for url in urls])


@blueprint.post("/")
@doc.consumes(doc.JsonBody({"key": str, "lines": [str]}), location="body")
async def create(request):
    url = request.app.url_for(
        "images.text",
        key=request.json["key"],
        slug=utils.text.encode(request.json["lines"]),
        _external=True,
    )
    return response.json({"url": url}, status=201)


@blueprint.get("/<key>.png")
async def blank(request, key):
    return await render_image(request, key)


@blueprint.get("/<key>.jpg")
async def blank_jpg(request, key):
    return await render_image(request, key, ext="jpg")


@blueprint.get("/<key>/<slug:path>.png")
async def text(request, key, slug):
    return await render_image(request, key, slug)


@blueprint.get("/<key>/<slug:path>.jpg")
async def text_jpg(request, key, slug):
    return await render_image(request, key, slug, ext="jpg")


async def render_image(
    request, key: str, slug: str = "", ext: str = settings.DEFAULT_EXT
):
    status = 200
    loop = asyncio.get_event_loop()

    if key == "custom":
        url = request.args.get("alt")
        if url:
            template = await models.Template.create(url)
            key = template.key
        else:
            logger.warn("No image URL specified for custom template")
            status = 422

    path = await loop.run_in_executor(None, save_image, key, slug, ext)

    return await response.file(path, status)
