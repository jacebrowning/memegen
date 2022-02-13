import asyncio
from contextlib import suppress
from dataclasses import dataclass

from sanic import Blueprint, exceptions, response
from sanic_ext import openapi

from .. import helpers, settings, utils
from ..models import Template

blueprint = Blueprint("Templates", url_prefix="/templates")


@dataclass
class ExampleResponse:
    text: list[str]
    url: str


@dataclass
class TemplateResponse:
    id: str
    name: str
    lines: int
    overlays: int
    styles: list[str]
    blank: str
    example: ExampleResponse
    source: str
    _self: str


@blueprint.get("/")
@openapi.summary("List all templates")
@openapi.parameter(
    "animated",
    bool,
    "query",
    description="Limit results to templates supporting animation",
)
@openapi.parameter(
    "filter", str, "query", description="Part of the name or example to match"
)
@openapi.response(
    200,
    {"application/json": list[TemplateResponse]},
    "Successfully returned a list of all templates",
)
async def index(request):
    query = request.args.get("filter", "").lower()
    animated = utils.urls.flag(request, "animated")
    data = await asyncio.to_thread(
        helpers.get_valid_templates, request, query, animated
    )
    return response.json(data)


@blueprint.get("/<id:slug>")
@openapi.summary("View a specific template")
@openapi.parameter("id", str, "path")
@openapi.response(
    200,
    {"application/json": TemplateResponse},
    "Successfully returned a specific templates",
)
@openapi.response(404, str, description="Template not found")
async def detail(request, id):
    template: Template = Template.objects.get_or_none(id)
    if template:
        return response.json(template.jsonify(request))
    raise exceptions.NotFound(f"Template not found: {id}")


@dataclass
class MemeRequest:
    text_lines: list[str]
    extension: str
    redirect: bool


@dataclass
class MemeResponse:
    url: str


@blueprint.post("/<id:slug>")
@openapi.tag("Memes")
@openapi.operation("Memes.create_from_template")
@openapi.exclude(settings.DEPLOYED)
@openapi.summary("Create a meme from a template" + settings.SUFFIX)
@openapi.parameter("id", str, "path")
@openapi.body({"application/json": MemeRequest})
@openapi.response(
    201,
    {"application/json": MemeResponse},
    "Successfully created a meme from a template",
)
async def build(request, id):
    return await generate_url(request, id)


@dataclass
class CustomRequest:
    background: str
    style: str
    text_lines: list[str]
    font: str
    extension: str
    redirect: bool


@blueprint.post("/custom")
@openapi.tag("Memes")
@openapi.exclude(settings.DEPLOYED)
@openapi.summary("Create a meme from any image" + settings.SUFFIX)
@openapi.body({"application/json": CustomRequest})
@openapi.response(
    201,
    {"application/json": MemeResponse},
    "Successfully created a meme from a custom image",
)
async def custom(request):
    return await generate_url(request)


async def generate_url(
    request, template_id: str = "", *, template_id_required: bool = False
):
    if request.form:
        payload = dict(request.form)
        for key in list(payload.keys()):
            if "lines" not in key and "style" not in key:
                payload[key] = payload.pop(key)[0]
    else:
        try:
            payload = request.json or {}
        except exceptions.InvalidUsage:
            payload = {}

    with suppress(KeyError):
        payload["style"] = payload.pop("style[]")
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    if template_id_required:
        try:
            template_id = payload["template_id"]
        except KeyError:
            return response.json({"error": '"template_id" is required'}, status=400)
        else:
            template_id = utils.text.slugify(template_id)

    style: str = utils.urls.arg(payload, "", "style", "overlay", "alt")
    if isinstance(style, list):
        style = ",".join([(s.strip() or "default") for s in style])
    while style.endswith(",default"):
        style = style.removesuffix(",default")
    text_lines = utils.urls.arg(payload, [], "text_lines")
    font = utils.urls.arg(payload, "", "font")
    background = utils.urls.arg(payload, "", "background", "image_url")
    extension = utils.urls.arg(payload, "", "extension")

    if style == "animated":
        extension = "gif"
        style = ""

    status = 201

    if template_id:
        template: Template = Template.objects.get_or_create(template_id)
        url = template.build_custom_url(
            request,
            text_lines,
            style=style,
            font=font,
            extension=extension,
        )
        if not template.valid:
            status = 404
            template.delete()
    else:
        template = Template("_custom")
        url = template.build_custom_url(
            request,
            text_lines,
            background=background,
            style=style,
            font=font,
            extension=extension,
        )

    url, _updated = await utils.meta.tokenize(request, url)

    if payload.get("redirect", False):
        return response.redirect(utils.urls.add(url, status="201"))

    return response.json({"url": url}, status=status)
