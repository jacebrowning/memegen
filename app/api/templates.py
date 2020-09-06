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
async def index(request):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, helpers.get_valid_templates, request)
    return response.json(data)


@blueprint.get("/<key>")
@doc.summary("View a specific template")
async def detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.jsonify(request.app))
    abort(404)


@blueprint.post("/custom")
@doc.summary("Create a meme from any image")
@doc.consumes(doc.JsonBody({"image_url": str, "text_lines": [str]}), location="body")
async def custom(request):
    if request.form:
        payload = dict(request.form)
        with suppress(KeyError):
            payload["text_lines"] = payload.pop("text_lines[]")
    else:
        payload = request.json

    url = Template("_custom").build_custom_url(
        request.app,
        payload.get("text_lines") or [],
        background=payload["image_url"],
    )
    return response.json({"url": url}, status=201)


@blueprint.post("/<key>")
@doc.summary("Create a meme from a template")
@doc.consumes(doc.JsonBody({"text_lines": [str]}), location="body")
async def build(request, key):
    if request.form:
        payload = dict(request.form)
        with suppress(KeyError):
            payload["text_lines"] = payload.pop("text_lines[]")
    else:
        payload = request.json

    template = Template.objects.get(key)
    url = template.build_custom_url(request.app, payload.get("text_lines") or [])
    return response.json({"url": url}, status=201)
