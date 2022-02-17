import asyncio

from sanic import Blueprint, exceptions, response
from sanic_ext import openapi

from .. import helpers, utils
from ..models import Template
from .helpers import generate_url
from .schemas import CustomRequest, MemeResponse, MemeTemplateRequest, TemplateResponse

blueprint = Blueprint("templates", url_prefix="/templates")


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
@openapi.parameter("id", str, "path", description="ID of a meme template")
@openapi.response(
    200,
    {"application/json": TemplateResponse},
    "Successfully returned a specific template",
)
@openapi.response(404, str, description="Template not found")
async def detail(request, id):
    template: Template = Template.objects.get_or_none(id)
    if template:
        return response.json(template.jsonify(request))
    raise exceptions.NotFound(f"Template not found: {id}")


@blueprint.post("/<id:slug>")
@openapi.summary("Create a meme from a template")
@openapi.parameter("id", str, "path", description="ID of a meme template")
@openapi.body({"application/json": MemeTemplateRequest})
@openapi.response(
    201,
    {"application/json": MemeResponse},
    "Successfully created a meme from a template",
)
async def build(request, id):
    return await generate_url(request, id)


@blueprint.post("/custom")
@openapi.summary("Create a meme from any image")
@openapi.body({"application/json": CustomRequest})
@openapi.response(
    201,
    {"application/json": MemeResponse},
    "Successfully created a meme from a custom image",
)
async def custom(request):
    return await generate_url(request)
