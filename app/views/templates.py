import asyncio

from sanic import Blueprint, exceptions, response
from sanic.request import Request
from sanic_ext import openapi

from .. import helpers, utils
from ..models import Template
from .helpers import generate_url
from .schemas import CustomRequest, MemeResponse, MemeTemplateRequest, TemplateResponse

blueprint = Blueprint("Templates", url_prefix="/templates")


@blueprint.get("/")
@openapi.summary("List all templates")
@openapi.description(
    "The full list of renderable templates. For URL construction, the four "
    "load-bearing fields per template are `id` (goes into the path after "
    "`/images/`), `lines` (maximum number of `/`-separated text segments "
    "accepted in the path), `overlays` (number of overlay image slots the "
    "template defines), and `styles` (allowed values for the `style=` query "
    "parameter). The remaining fields are descriptive: `name` for display, "
    "`blank` for the empty-template render URL, `example.url` for a "
    "guaranteed-valid smoke-test URL, `source` for attribution, and "
    "`keywords` for search. Recommended client pattern: fetch this endpoint "
    "once at startup, cache, and construct URLs locally rather than per-meme. "
    "See `docs/guide.md` for worked examples and the full escape table."
)
@openapi.parameter(
    "animated",
    bool,
    "query",
    description="Limit results to templates supporting animation",
)
@openapi.parameter(
    "filter", str, "query", description="Part of the name, keyword, or example to match"
)
@openapi.response(
    200,
    {"application/json": list[TemplateResponse]},
    "Successfully returned a list of all templates",
)
async def index(request: Request):
    query = request.args.get("filter", "").lower()
    animated = utils.urls.flag(request, "animated")
    data = await asyncio.to_thread(
        helpers.get_valid_templates, request, query, animated
    )
    return response.json(data)


@blueprint.get("/<id:slug>")
@openapi.summary("View a specific template")
@openapi.description(
    "Per-template metadata. The four URL-construction fields are `id`, "
    "`lines`, `overlays`, and `styles`; see `GET /templates/` for what each "
    "one governs and `docs/guide.md` for worked examples. The `example.url` "
    "field is a guaranteed-valid render URL — issuing a `HEAD` against it is "
    "the cheapest way to validate that the template id is live."
)
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
async def custom(request: Request):
    return await generate_url(request)
