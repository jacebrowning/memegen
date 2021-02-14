import asyncio
from contextlib import suppress
from urllib.parse import parse_qs, urlparse

from sanic import Blueprint, response
from sanic.log import logger
from sanic_openapi import doc

from .. import helpers, models, settings, utils

blueprint = Blueprint("Memes", url_prefix="/images")


@blueprint.get("/")
@doc.summary("List example memes")
@doc.operation("Memes.list")
# TODO: https://github.com/jacebrowning/memegen/issues/580
# @doc.consumes(
#     doc.String(
#         name="filter", description="Part of the template name or example to match"
#     ),
#     location="query",
# )
@doc.produces(
    doc.List({"url": str, "template": str}),
    description="Successfully returned a list of example memes",
    content_type="application/json",
)
async def index(request):
    query = request.args.get("filter", "").lower()
    examples = await asyncio.to_thread(helpers.get_example_images, request, query)
    return response.json(
        [{"url": url, "template": template} for url, template in examples]
    )


@blueprint.post("/")
@doc.summary("Create a meme from a template")
@doc.operation("Memes.create")
@doc.consumes(
    doc.JsonBody(
        {"template_id": str, "text_lines": [str], "extension": str, "redirect": bool}
    ),
    content_type="application/json",
    location="body",
)
@doc.response(201, {"url": str}, description="Successfully created a meme")
@doc.response(
    400, {"error": str}, description='Required "template_id" missing in request body'
)
@doc.response(404, {"error": str}, description='Specified "template_id" does not exist')
async def create(request):
    if request.form:
        payload = dict(request.form)
        with suppress(KeyError):
            payload["template_id"] = payload.pop("template_id")[0]
        with suppress(KeyError):
            payload["extension"] = payload.pop("extension")[0]
        with suppress(KeyError):
            payload["redirect"] = payload.pop("redirect")[0]
    else:
        payload = request.json or {}
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    try:
        template_id = payload["template_id"]
    except KeyError:
        return response.json({"error": '"template_id" is required'}, status=400)

    template = models.Template.objects.get_or_create(template_id)
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


@blueprint.post("/automatic")
@doc.exclude(settings.DEPLOYED)
@doc.summary(settings.PREFIX + "Create a meme from word or phrase")
@doc.consumes(
    doc.JsonBody({"text": str, "redirect": bool}),
    content_type="application/json",
    location="body",
)
@doc.response(201, {"url": str}, description="Successfully created a meme")
@doc.response(
    400, {"error": str}, description='Required "text" missing in request body'
)
async def auto(request):
    if request.form:
        payload = dict(request.form)
    else:
        payload = request.json or {}

    try:
        text = payload["text"]
    except KeyError:
        return response.json({"error": '"text" is required'}, status=400)

    results = await utils.meta.search(request, text)
    logger.info(f"Found {len(results)} result(s)")
    if not results:
        return response.json({"message": f"No results matched: {text}"}, status=404)

    parts = urlparse(results[0]["image_url"])
    url = f"{settings.BASE_URL}{parts.path}"
    if "background" in parts.query:
        url += "?background=" + parse_qs(parts.query)["background"][0]
    logger.info(f"Top result: {url}")

    if payload.get("redirect", False):
        return response.redirect(url)

    return response.json({"url": url}, status=201)


@blueprint.post("/custom")
@doc.summary("Create a meme from any image")
@doc.consumes(
    doc.JsonBody(
        {"image_url": str, "text_lines": [str], "extension": str, "redirect": bool}
    ),
    content_type="application/json",
    location="body",
)
@doc.response(
    201, {"url": str}, description="Successfully created a meme from a custom image"
)
async def custom(request):
    if request.form:
        payload = dict(request.form)
        with suppress(KeyError):
            payload["image_url"] = payload.pop("image_url")[0]
        with suppress(KeyError):
            payload["extension"] = payload.pop("extension")[0]
        with suppress(KeyError):
            payload["redirect"] = payload.pop("redirect")[0]
    else:
        payload = request.json or {}
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    url = models.Template("_custom").build_custom_url(
        request.app,
        payload.get("text_lines") or [],
        background=payload.get("image_url", ""),
        extension=payload.get("extension", ""),
    )

    if payload.get("redirect", False):
        return response.redirect(url)

    return response.json({"url": url}, status=201)


@blueprint.get("/<template_id>.png")
@doc.tag("Templates")
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
async def blank_png(request, template_id):
    return await render_image(request, template_id, ext="png")


@blueprint.get("/<template_id>.jpg")
@doc.tag("Templates")
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
async def blank_jpg(request, template_id):
    return await render_image(request, template_id, ext="jpg")


@blueprint.get("/<template_id>/<text_paths:[\\s\\S]+>.png")
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
async def text_png(request, template_id, text_paths):
    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "Memes.text_png",
            template_id=template_id,
            text_paths=slug,
            **request.args,
        )
        return response.redirect(utils.text.unquote(url), status=301)

    watermark, updated = utils.meta.get_watermark(
        request, request.args.get("watermark")
    )
    if updated:
        url = request.app.url_for(
            "Memes.text_png",
            template_id=template_id,
            text_paths=slug,
            **{k: v for k, v in request.args.items() if k != "watermark"},
        )
        return response.redirect(utils.text.unquote(url), status=301)

    return await render_image(request, template_id, slug, watermark)


@blueprint.get("/<template_id>/<text_paths:[\\s\\S]+>.jpg")
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
async def text_jpg(request, template_id, text_paths):
    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "Memes.text_jpg",
            template_id=template_id,
            text_paths=slug,
            **request.args,
        )
        return response.redirect(utils.text.unquote(url), status=301)

    watermark, updated = utils.meta.get_watermark(
        request, request.args.get("watermark")
    )
    if updated:
        url = request.app.url_for(
            "Memes.text_jpg",
            template_id=template_id,
            text_paths=slug,
            **{k: v for k, v in request.args.items() if k != "watermark"},
        )
        return response.redirect(utils.text.unquote(url), status=301)

    return await render_image(request, template_id, slug, watermark, ext="jpg")


async def render_image(
    request,
    id: str,
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

    elif id == "custom":
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
        template = models.Template.objects.get_or_none(id)
        if not template or not template.image.exists():
            logger.error(f"No such template: {id}")
            template = models.Template.objects.get("_error")
            status = 404

        style = request.args.get("style") or request.args.get("alt")
        if style and style not in template.styles:
            logger.error(f"Invalid style for template: {style}")
            status = 422

    lines = utils.text.decode(slug)
    size = int(request.args.get("width", 0)), int(request.args.get("height", 0))

    asyncio.create_task(utils.meta.track(request, lines))
    path = await asyncio.to_thread(
        utils.images.save, template, lines, watermark, ext=ext, style=style, size=size
    )
    return await response.file(path, status)
