import asyncio

from sanic import Blueprint, response
from sanic.log import logger
from sanic_openapi import doc

from .. import models, settings, utils

blueprint = Blueprint("Clients", url_prefix="/")


@blueprint.post("/auth")
@doc.summary("Validate your API key")
@doc.response(200, str, description="Your API key is valid")
@doc.response(401, str, description="Your API key is invalid")
async def validate(request):
    info = await utils.meta.authenticate(request)
    return response.json(
        info or {"error": "API key missing or invalid."},
        status=200 if info else 401,
    )


@blueprint.get("/images/preview.jpg")
@doc.summary("Display a preview of a custom meme")
@doc.consumes(
    doc.String(name="lines[]", description="Lines of text to render"),
    location="query",
)
@doc.consumes(
    doc.String(name="style", description="Style name or custom overlay"),
    location="query",
)
@doc.consumes(
    doc.String(name="template", description="Template ID, URL, or custom background"),
    location="query",
)
@doc.produces(
    doc.File(),
    description="Successfully displayed a custom meme",
    content_type="image/jpeg",
)
async def preview(request):
    id = request.args.get("template", "_error")
    lines = request.args.getlist("lines[]", [])
    style = request.args.get("style") or settings.DEFAULT_STYLE
    return await preview_image(request, id, lines, style)


async def preview_image(request, id: str, lines: list[str], style: str):
    id = utils.urls.clean(id)
    if utils.urls.schema(id):
        template = await models.Template.create(id)
        if not template.image.exists():
            logger.error(f"Unable to download image URL: {id}")
            template = models.Template.objects.get("_error")
    else:
        template = models.Template.objects.get_or_none(id)
        if not template:
            logger.error(f"No such template: {id}")
            template = models.Template.objects.get("_error")

    if not utils.urls.schema(style):
        style = style.lower()
    await template.check(style)

    data, content_type = await asyncio.to_thread(
        utils.images.preview, template, lines, style=style
    )
    return response.raw(data, content_type=content_type)
