from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic_openapi import doc

from ..models import Template

blueprint = Blueprint("templates", url_prefix="/api/templates")


@blueprint.get("/")
async def index(request):
    templates = Template.objects.filter(valid=True)
    return response.json([t.jsonify(request.app) for t in templates])


@blueprint.get("/<key>")
async def detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.jsonify(request.app))
    abort(404)
