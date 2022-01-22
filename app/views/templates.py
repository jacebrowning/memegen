import asyncio
from contextlib import suppress

from sanic import Blueprint, exceptions, response
from sanic_openapi import doc

from .. import helpers, settings, utils
from ..models import Template

blueprint = Blueprint("Templates", url_prefix="/templates")

TemplateResponse = {
    "id": str,
    "name": str,
    "lines": int,
    "overlays": int,
    "styles": doc.List(str),
    "blank": str,
    "example": {
        "text": doc.List(str),
        "url": str,
    },
    "source": str,
    "_self": str,
}


@blueprint.get("/")
@doc.summary("List all templates")
@doc.consumes(
    doc.Boolean(
        name="animated", description="Limit results to templates supporting animation"
    ),
    content_type="application/json",
    location="query",
)
@doc.consumes(
    doc.String(name="filter", description="Part of the name or example to match"),
    location="query",
)
@doc.produces(
    doc.List(TemplateResponse),
    description="Successfully returned a list of all templates",
    content_type="application/json",
)
async def index(request):
    query = request.args.get("filter", "").lower()
    animated = utils.urls.flag(request, "animated")
    data = await asyncio.to_thread(
        helpers.get_valid_templates, request, query, animated
    )
    return response.json(data)


@blueprint.get("/<id:slug>")
@doc.summary("View a specific template")
@doc.consumes(doc.String(name="id"), location="path")
@doc.produces(
    TemplateResponse,
    description="Successfully returned a specific templates",
    content_type="application/json",
)
@doc.response(404, str, description="Template not found")
async def detail(request, id):
    template: Template = Template.objects.get_or_none(id)
    if template:
        return response.json(template.jsonify(request))
    raise exceptions.NotFound(f"Template not found: {id}")


@blueprint.post("/<id:slug>")
@doc.tag("Memes")
@doc.operation("Memes.create_from_template")
@doc.exclude(settings.DEPLOYED)
@doc.summary("Create a meme from a template" + settings.SUFFIX)
@doc.consumes(doc.String(name="id"), location="path")
@doc.consumes(
    doc.JsonBody({"text_lines": [str], "extension": str, "redirect": bool}),
    content_type="application/json",
    location="body",
)
@doc.response(
    201, {"url": str}, description="Successfully created a meme from a template"
)
async def build(request, id):
    return await generate_url(request, id)


@blueprint.post("/custom")
@doc.tag("Memes")
@doc.exclude(settings.DEPLOYED)
@doc.summary("Create a meme from any image" + settings.SUFFIX)
@doc.consumes(
    doc.JsonBody(
        {
            "background": str,
            "style": str,
            "text_lines": [str],
            "extension": str,
            "redirect": bool,
        }
    ),
    content_type="application/json",
    location="body",
)
@doc.response(
    201, {"url": str}, description="Successfully created a meme from a custom image"
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
        payload["text_lines"] = payload.pop("text_lines[]")
    with suppress(KeyError):
        payload["style"] = payload.pop("style[]")

    if template_id_required:
        try:
            template_id = payload["template_id"]
        except KeyError:
            return response.json({"error": '"template_id" is required'}, status=400)
        else:
            template_id = utils.text.slugify(template_id)

    text_lines = utils.urls.arg(payload, [], "text_lines")
    style: str = utils.urls.arg(payload, "", "style", "overlay", "alt")
    if isinstance(style, list):
        style = ",".join([(s.strip() or "default") for s in style])
    while style.endswith(",default"):
        style = style.removesuffix(",default")
    background = utils.urls.arg(payload, "", "background", "image_url")
    extension = utils.urls.arg(payload, "", "extension")

    if style == "animated":
        extension = "gif"
        style = ""

    status = 201

    if template_id:
        template: Template = Template.objects.get_or_create(template_id)
        url = template.build_custom_url(
            request, text_lines, style=style, extension=extension
        )
        if not template.valid:
            status = 404
            template.delete()
    else:
        template = Template("_custom")
        url = template.build_custom_url(
            request, text_lines, background=background, style=style, extension=extension
        )

    url, _updated = await utils.meta.tokenize(request, url)

    if payload.get("redirect", False):
        return response.redirect(utils.urls.add(url, status="201"))

    return response.json({"url": url}, status=status)
