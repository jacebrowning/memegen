import asyncio

from sanic import Blueprint, response
from sanic.log import logger
from sanic_openapi import doc

from .. import helpers, models, settings, utils

blueprint = Blueprint("images", url_prefix="/api/images")


@blueprint.get("/")
async def index(request):
    loop = asyncio.get_event_loop()
    urls = await loop.run_in_executor(None, helpers.get_sample_images, request)
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
    slug, updated = utils.text.normalize(slug)
    if updated:
        url = request.app.url_for(
            "images.text", key=key, slug=slug, **request.args
        ).replace("%3A%2F%2F", "://")
        return response.redirect(url, status=301)
    return await render_image(request, key, slug)


@blueprint.get("/<key>/<slug:path>.jpg")
async def text_jpg(request, key, slug):
    slug, updated = utils.text.normalize(slug)
    if updated:
        url = request.app.url_for(
            "images.text_jpg", key=key, slug=slug, **request.args
        ).replace("%3A%2F%2F", "://")
        return response.redirect(url, status=301)
    return await render_image(request, key, slug, ext="jpg")


async def render_image(
    request, key: str, slug: str = "", ext: str = settings.DEFAULT_EXT
):
    status = 200

    if key == "custom":
        url = request.args.get("alt")
        if url:
            template = await models.Template.create(url)
            if not template.image.exists():
                logger.error(f"Unable to download image URL: {url}")
                template = models.Template.objects.get("_error")
                status = 415
        else:
            logger.error("No image URL specified for custom template")
            template = models.Template.objects.get("_error")
            status = 422
    else:
        template = models.Template.objects.get_or_none(key)
        if not template:
            logger.error(f"No such template: {key}")
            template = models.Template.objects.get("_error")
            status = 404

    lines = utils.text.decode(slug)

    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, utils.images.save, template, lines, ext)

    return await response.file(path, status)
