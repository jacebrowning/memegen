import asyncio
from dataclasses import dataclass
from datetime import datetime

from sanic import Blueprint, response
from sanic.log import logger
from sanic_ext import openapi

from .. import models, utils

blueprint = Blueprint("Clients", url_prefix="/")


@dataclass
class AuthResponse:
    email: str
    image_access: bool
    search_access: bool
    created: datetime
    modified: datetime


@dataclass
class ErrorResponse:
    error: str


@blueprint.post("/auth")
@openapi.summary("Validate your API key")
@openapi.response(200, {"application/json": AuthResponse}, "Your API key is valid")
@openapi.response(401, {"application/json": ErrorResponse}, "Your API key is invalid")
async def validate(request):
    info = await utils.meta.authenticate(request)
    return response.json(
        info or {"error": "API key missing or invalid."},
        status=200 if info else 401,
    )


@dataclass
class FontResponse:
    filename: str
    id: str
    alias: str


@blueprint.get("/fonts")
@openapi.summary("List available fonts")
@openapi.response(
    200,
    {"application/json": list[FontResponse]},
    "Successfully returned a list of fonts",
)
async def fonts(request):
    return response.json([font.data for font in models.Font.objects.all()])


@blueprint.get("/images/preview.jpg")
@openapi.summary("Display a preview of a custom meme")
@openapi.parameter("lines[]", str, "query", description="Lines of text to render")
@openapi.parameter("style", str, "query", description="Style name or custom overlay")
@openapi.parameter(
    "template", str, "query", description="Template ID, URL, or custom background"
)
@openapi.response(200, {"image/jpeg": bytes}, "Successfully displayed a custom meme")
async def preview(request):
    id = request.args.get("template", "_error")
    lines = request.args.getlist("lines[]", [])
    style = request.args.get("style") or ",".join(request.args.getlist("styles[]", []))
    while style.endswith(",default"):
        style = style.removesuffix(",default")
    return await preview_image(request, id, lines, style)


async def preview_image(request, id: str, lines: list[str], style: str):
    error = ""

    id = utils.urls.clean(id)
    if utils.urls.schema(id):
        template = await models.Template.create(id)
        if not template.image.exists():
            logger.error(f"Unable to download image URL: {id}")
            template = models.Template.objects.get("_error")
            error = "Invalid Background"
    else:
        template = models.Template.objects.get_or_none(id)
        if not template:
            logger.error(f"No such template: {id}")
            template = models.Template.objects.get("_error")
            error = "Unknown Template"

    if not any(line.strip() for line in lines):
        lines = template.example

    if not utils.urls.schema(style):
        style = style.strip().lower()
    if not await template.check(style):
        error = "Invalid Overlay"

    data, content_type = await asyncio.to_thread(
        utils.images.preview, template, lines, style=style, watermark=error.upper()
    )
    return response.raw(data, content_type=content_type)
