import asyncio
from contextlib import suppress
from typing import List

from sanic import Blueprint, response
from sanic.log import logger
from sanic_openapi import doc

from .. import helpers, models, settings, utils

blueprint = Blueprint("images", url_prefix="/images")


@blueprint.get("/")
@doc.summary("List example memes")
@doc.operation("images.list")
@doc.produces(
    doc.List({"url": str, "template": str}),
    description="Successfully returned a list of example memes",
    content_type="application/json",
)
async def index(request):
    examples = await asyncio.to_thread(helpers.get_example_images, request)
    return response.json(
        [{"url": url, "template": template} for url, template in examples]
    )


@blueprint.post("/")
@doc.summary("Create a meme from a template")
@doc.operation("images.create")
@doc.consumes(
    doc.JsonBody(
        {"template_key": str, "text_lines": [str], "extension": str, "redirect": bool}
    ),
    content_type="application/json",
    location="body",
)
@doc.response(201, {"url": str}, description="Successfully created a meme")
@doc.response(
    400, {"error": str}, description='Required "template_key" missing in request body'
)
@doc.response(
    404, {"error": str}, description='Specified "template_key" does not exist'
)
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

    template = models.Template.objects.get_or_create(template_key)
    url = template.build_custom_url(
        request.app,
        payload.get("text_lines") or [],
        extension=payload.get("extension"),
    )

    if payload.get("redirect", False):
        return response.redirect(url)

    if template.valid:
        status = 201
    else:
        status = 404
        template.delete()

    return response.json({"url": url}, status=status)


@blueprint.get("/preview.jpg")
@doc.summary("Display a preview of a custom meme")
@doc.produces(
    doc.File(),
    description="Successfully displayed a custom meme",
    content_type="image/jpeg",
)
async def preview(request):
    key = request.args.get("template", "_error")
    lines = request.args.getlist("lines[]", [])
    style = request.args.get("style")
    return await preview_image(request, key, lines, style)


@blueprint.get("/<template_key>.png")
@doc.summary("Display a template background")
@doc.produces(
    doc.File(),
    description="Successfully displayed a template background",
    content_type="image/png",
)
@doc.response(404, doc.File(), description="Template not found")
@doc.response(415, doc.File(), description="Unable to download image URL")
@doc.response(
    422,
    doc.File(),
    description="Invalid style for template or no image URL specified for custom template",
)
async def blank_png(request, template_key):
    return await render_image(request, template_key, ext="png")


@blueprint.get("/<template_key>.jpg")
@doc.summary("Display a template background")
@doc.produces(
    doc.File(),
    description="Successfully displayed a template background",
    content_type="image/jpeg",
)
@doc.response(404, doc.File(), description="Template not found")
@doc.response(415, doc.File(), description="Unable to download image URL")
@doc.response(
    422,
    doc.File(),
    description="Invalid style for template or no image URL specified for custom template",
)
async def blank_jpg(request, template_key):
    return await render_image(request, template_key, ext="jpg")


@blueprint.get("/<template_key>/<text_paths:[\s\S]+>.png")
@doc.summary("Display a custom meme")
@doc.produces(
    doc.File(),
    description="Successfully displayed a custom meme",
    content_type="image/png",
)
@doc.response(404, doc.File(), description="Template not found")
@doc.response(414, doc.File(), description="Custom text too long (length >200)")
@doc.response(415, doc.File(), description="Unable to download image URL")
@doc.response(
    422,
    doc.File(),
    description="Invalid style for template or no image URL specified for custom template",
)
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

    watermark, updated = utils.meta.get_watermark(
        request, request.args.get("watermark")
    )
    if updated:
        url = request.app.url_for(
            "images.text_png",
            template_key=template_key,
            text_paths=slug,
            **{k: v for k, v in request.args.items() if k != "watermark"},
        ).replace("%3A%2F%2F", "://")
        return response.redirect(url, status=301)

    return await render_image(request, template_key, slug, watermark)


@blueprint.get("/<template_key>/<text_paths:[\s\S]+>.jpg")
@doc.summary("Display a custom meme")
@doc.produces(
    doc.File(),
    description="Successfully displayed a custom meme",
    content_type="image/jpeg",
)
@doc.response(404, doc.File(), description="Template not found")
@doc.response(414, doc.File(), description="Custom text too long (length >200)")
@doc.response(415, doc.File(), description="Unable to download image URL")
@doc.response(
    422,
    doc.File(),
    description="Invalid style for template or no image URL specified for custom template",
)
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

    watermark, updated = utils.meta.get_watermark(
        request, request.args.get("watermark")
    )
    if updated:
        url = request.app.url_for(
            "images.text_jpg",
            template_key=template_key,
            text_paths=slug,
            **{k: v for k, v in request.args.items() if k != "watermark"},
        ).replace("%3A%2F%2F", "://")
        return response.redirect(url, status=301)

    return await render_image(request, template_key, slug, watermark, ext="jpg")


async def preview_image(request, key: str, lines: List[str], style: str):
    if "://" in key:
        template = await models.Template.create(key)
    else:
        template = models.Template.objects.get(key)

    data, content_type = await asyncio.to_thread(
        utils.images.preview, template, lines, style=style
    )
    return response.raw(data, content_type=content_type)


async def render_image(
    request,
    key: str,
    slug: str = "",
    watermark: str = "",
    ext: str = settings.DEFAULT_EXT,
):
    status = 200

    if len(slug.encode()) > 200:
        logger.error(f"Slug too long: {slug}")
        slug = slug[:50] + "..."
        template = models.Template.objects.get("_error")
        style = settings.DEFAULT_STYLE
        status = 414

    elif key == "custom":
        style = settings.DEFAULT_STYLE
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

    await utils.meta.track_url(request, lines)
    path = await asyncio.to_thread(
        utils.images.save, template, lines, watermark, ext=ext, style=style, size=size
    )
    return await response.file(path, status)
