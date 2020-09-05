import asyncio
from contextlib import suppress

from sanic import Blueprint, response
from sanic.log import logger
from sanic_openapi import doc

from .. import helpers, models, settings, utils

blueprint = Blueprint("images", url_prefix="/images")


@blueprint.get("/")
@doc.tag("samples")
@doc.summary("List sample memes")
async def index(request):
    loop = asyncio.get_event_loop()
    samples = await loop.run_in_executor(None, helpers.get_sample_images, request)
    return response.json(
        [{"url": url, "template": template} for url, template in samples]
    )


@blueprint.post("/")
@doc.tag("memes")
@doc.summary("Create a meme from a template")
@doc.consumes(doc.JsonBody({"template_key": str, "text_lines": [str]}), location="body")
async def create(request):
    if request.form:
        payload = dict(request.form)
        with suppress(KeyError):
            payload["template_key"] = payload.pop("template_key")[0]
        with suppress(KeyError):
            payload["text_lines"] = payload.pop("text_lines[]")
    else:
        payload = request.json

    try:
        template_key = payload["template_key"]
    except KeyError:
        return response.json({"error": '"template_key" is required'}, status=400)

    url = request.app.url_for(
        f"images.text_{settings.DEFAULT_EXT}",
        template_key=template_key,
        text_paths=utils.text.encode(payload.get("text_lines") or []),
        _external=True,
    )
    return response.json({"url": url}, status=201)


@blueprint.get("/<template_key>.png")
@doc.summary("Display a template background")
async def blank_png(request, template_key):
    return await render_image(request, template_key, ext="png")


@blueprint.get("/<template_key>.jpg")
@doc.summary("Display a template background")
async def blank_jpg(request, template_key):
    return await render_image(request, template_key, ext="jpg")


@blueprint.get("/<template_key>/<text_paths:path>.png")
@doc.summary("Display a custom meme")
async def text_png(request, template_key, text_paths):
    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "images.text_png",
            template_key=template_key,
            text_paths=slug,
            **request.args,
        ).replace("%3A%2F%2F", "://")
        return response.redirect(url, status=301)
    return await render_image(request, template_key, slug)


@blueprint.get("/<template_key>/<text_paths:path>.jpg")
@doc.summary("Display a custom meme")
async def text_jpg(request, template_key, text_paths):
    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "images.text_jpg",
            template_key=template_key,
            text_paths=slug,
            **request.args,
        ).replace("%3A%2F%2F", "://")
        return response.redirect(url, status=301)
    return await render_image(request, template_key, slug, ext="jpg")


async def render_image(
    request, key: str, slug: str = "", ext: str = settings.DEFAULT_EXT
):
    status = 200

    if key == "custom":
        style = "default"
        url = request.args.get("background") or request.args.get("alt")
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

        style = request.args.get("style") or request.args.get("alt")
        if style and style not in template.styles:
            logger.error(f"Invalid style for template: {style}")
            status = 422

    lines = utils.text.decode(slug)

    size = int(request.args.get("width", 0)), int(request.args.get("height", 0))

    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(
        None, utils.images.save, template, lines, ext, style, size
    )

    return await response.file(path, status)
