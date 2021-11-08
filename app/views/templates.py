import asyncio
from contextlib import suppress

from sanic import Blueprint, exceptions, response
from sanic_openapi import doc

from .. import helpers, settings, utils
from ..models import Template

blueprint = Blueprint("Templates", url_prefix="/templates")


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
    # Can't use doc.List(Template) because the jsonify method is slightly different
    doc.List(
        {
            "id": str,
            "name": str,
            "styles": doc.List(str),
            "blank": str,
            "example": str,
            "source": str,
            "_self": str,
        }
    ),
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
    {
        "id": str,
        "name": str,
        "styles": doc.List(str),
        "blank": str,
        "example": str,
        "source": str,
        "_self": str,
    },
    description="Successfully returned a specific templates",
    content_type="application/json",
)
@doc.response(404, str, description="Template not found")
async def detail(request, id):
    template = Template.objects.get_or_none(id)
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
            if "lines" not in key:
                payload[key] = payload.pop(key)[0]
    else:
        payload = request.json or {}
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    if template_id_required:
        try:
            template_id = payload["template_id"]
        except KeyError:
            return response.json({"error": '"template_id" is required'}, status=400)

    text_lines = payload.get("text_lines") or []
    style = payload.get("style") or payload.get("alt")
    background = payload.get("background") or payload.get("image_url")
    extension = payload.get("extension")

    if style == "animated":
        extension = "gif"
        style = None

    status = 201

    if template_id:
        template = Template.objects.get_or_create(template_id)
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
        return response.redirect(url)

    return response.json({"url": url}, status=status)
