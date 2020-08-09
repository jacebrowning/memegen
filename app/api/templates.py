import asyncio

from sanic import Blueprint, response
from sanic.exceptions import abort

from .. import helpers
from ..models import Template

blueprint = Blueprint("templates", url_prefix="/api/templates")


@blueprint.get("/")
async def index(request):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, helpers.get_valid_templates, request)
    return response.json(data)


@blueprint.get("/<key>")
async def detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.jsonify(request.app))
    abort(404)
