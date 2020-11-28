import asyncio
from contextlib import suppress

from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic_openapi import doc

from .. import helpers
from ..models import Template

blueprint = Blueprint("templates", url_prefix="/templates")


@blueprint.get("/")
@doc.summary("List all templates")
@doc.produces(
    # Can't use doc.List(Template) because the jsonify method is slightly different
    doc.List(
        {
            "name": str,
            "key": str,
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
    data = await asyncio.to_thread(helpers.get_valid_templates, request)
    return response.json(data)


@blueprint.get("/<key>")
@doc.summary("View a specific template")
@doc.operation("templates.detail")
@doc.produces(
    {
        "name": str,
        "key": str,
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
async def detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.jsonify(request.app))
    abort(404)


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
        payload = request.json
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    url = Template("_custom").build_custom_url(
        request.app,
        payload.get("text_lines") or [],
        background=payload.get("image_url", ""),
        extension=payload.get("extension", ""),
    )

    if payload.get("redirect", False):
        return response.redirect(url)

    return response.json({"url": url}, status=201)


@blueprint.post("/<key>")
@doc.summary("Create a meme from a template")
@doc.operation("templates.create")
@doc.consumes(
    doc.JsonBody({"text_lines": [str], "extension": str, "redirect": bool}),
    content_type="application/json",
    location="body",
)
@doc.response(
    201, {"url": str}, description="Successfully created a meme from a template"
)
async def build(request, key):
    if request.form:
        payload = dict(request.form)
        with suppress(KeyError):
            payload["image_url"] = payload.pop("image_url")[0]
        with suppress(KeyError):
            payload["extension"] = payload.pop("extension")[0]
        with suppress(KeyError):
            payload["redirect"] = payload.pop("redirect")[0]
    else:
        payload = request.json
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    template = Template.objects.get(key)
    url = template.build_custom_url(
        request.app,
        payload.get("text_lines") or [],
        extension=payload.get("extension"),
    )

    if payload.get("redirect", False):
        return response.redirect(url)

    return response.json({"url": url}, status=201)
