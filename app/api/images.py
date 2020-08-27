import asyncio

from sanic import Blueprint, response
from sanic.exceptions import abort
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
    try:
        template_key = request.json["template_key"]
    except KeyError:
        return response.json({"error": '"template_key" is required'}, status=400)
    url = request.app.url_for(
        "images.text",
        template_key=template_key,
        text_paths=utils.text.encode(request.json.get("text_lines", [])),
        _external=True,
    )
    return response.json({"url": url}, status=201)


@blueprint.get("/<template_key>.png")
@doc.summary("Display a template background")
async def blank(request, template_key):
    return await render_image(request, template_key)


@blueprint.get("/<template_key>.jpg")
@doc.summary("Display a template background")
async def blank_jpg(request, template_key):
    return await render_image(request, template_key, ext="jpg")


@blueprint.get("/<template_key>")
@doc.summary("Display the sample image for a template")
async def sample(request, template_key):
    if settings.DEBUG:
        template = models.Template.objects.get_or_create(template_key)
    else:
        template = models.Template.objects.get_or_none(template_key)
    if template and template.valid:
        url = template.build_sample_url(request.app, "images.debug", external=False)
        return response.redirect(url)
    if settings.DEBUG:
        template.datafile.save()
        abort(501, f"Template not implemented: {template_key}")
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>/<text_paths:path>.png")
@doc.summary("Display a custom meme")
async def text(request, template_key, text_paths):
    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "images.text", template_key=template_key, text_paths=slug, **request.args
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


@blueprint.get("/<template_key>/<text_paths:path>")
@doc.exclude(True)
async def debug(request, template_key, text_paths):
    if not settings.DEBUG:
        url = request.app.url_for(
            "images.text", template_key=template_key, text_paths=text_paths
        )
        return response.redirect(url)

    template = models.Template.objects.get_or_create(template_key)
    template.datafile.save()
    url = f"/images/{template_key}/{text_paths}.png"
    content = utils.html.gallery([url], refresh=True, rate=1.0)
    return response.html(content)


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

    style = request.args.get("style")
    if style and style not in template.styles:
        status = 422

    size = int(request.args.get("width", 0)), int(request.args.get("height", 0))

    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(
        None, utils.images.save, template, lines, ext, style, size
    )

    return await response.file(path, status)
