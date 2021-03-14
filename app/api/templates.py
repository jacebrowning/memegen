import asyncio
from contextlib import suppress

from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic_openapi import doc

from .. import helpers, settings, utils
from ..models import Template

blueprint = Blueprint("Templates", url_prefix="/templates")


@blueprint.get("/")
@doc.summary("List all templates")
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
    data = await asyncio.to_thread(helpers.get_valid_templates, request, query)
    return response.json(data)


@blueprint.get("/<id>")
@doc.summary("View a specific template")
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
        return response.json(template.jsonify(request.app))
    abort(404)


@blueprint.post("/<id>")
@doc.tag("Memes")
@doc.operation("Memes.create_from_template")
@doc.exclude(settings.DEPLOYED)
@doc.summary(settings.PREFIX + "Create a meme from a template")
@doc.consumes(
    doc.JsonBody({"text_lines": [str], "extension": str, "redirect": bool}),
    content_type="application/json",
    location="body",
)
@doc.response(
    201, {"url": str}, description="Successfully created a meme from a template"
)
async def build(request, id):
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

    template = Template.objects.get_or_create(id)
    url = template.build_custom_url(
        request,
        payload.get("text_lines") or [],
        extension=payload.get("extension"),
    )
    url, _updated = await utils.meta.tokenize(request, url)

    if payload.get("redirect", False):
        return response.redirect(url)

    if template.valid:
        status = 201
    else:
        status = 404
        template.delete()

    return response.json({"url": url}, status=status)


@blueprint.post("/custom")
@doc.tag("Memes")
@doc.exclude(settings.DEPLOYED)
@doc.summary(settings.PREFIX + "Create a meme from any image")
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

    url = Template("_custom").build_custom_url(
        request,
        payload.get("text_lines") or [],
        background=payload.get("image_url", ""),
        extension=payload.get("extension", ""),
    )
    url, _updated = await utils.meta.tokenize(request, url)

    if payload.get("redirect", False):
        return response.redirect(url)

    return response.json({"url": url}, status=201)
