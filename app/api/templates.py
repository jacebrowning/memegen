import asyncio

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
