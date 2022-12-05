from sanic import Blueprint, response
from sanic.request import Request
from sanic_ext import openapi

from .. import utils
from .helpers import preview_image
from .schemas import AuthResponse, ErrorResponse

blueprint = Blueprint("Clients", url_prefix="/")


@blueprint.post("/auth")
@openapi.summary("Validate your API key")
@openapi.response(200, {"application/json": AuthResponse}, "Your API key is valid")
@openapi.response(401, {"application/json": ErrorResponse}, "Your API key is invalid")
async def validate(request: Request):
    info = await utils.meta.authenticate(request)
    return response.json(
        info or {"error": "API key missing or invalid."},
        status=200 if info else 401,
    )


@blueprint.get("/images/preview.jpg")
@openapi.summary("Display a preview of a custom meme")
@openapi.parameter("text[]", str, "query", description="Lines of text to render")
@openapi.parameter("style", str, "query", description="Style name or custom overlay")
@openapi.parameter(
    "template", str, "query", description="Template ID, URL, or custom background"
)
@openapi.parameter(
    "layout", str, "query", description="Text position: `default` or `top`"
)
@openapi.response(200, {"image/jpeg": bytes}, "Successfully displayed a custom meme")
async def preview(request: Request):
    id = request.args.get("template", "_error")
    lines = request.args.getlist("text[]") or request.args.getlist("lines[]") or []
    while lines and not lines[-1].strip():
        lines.pop(-1)
    style = request.args.get("style") or ",".join(request.args.getlist("styles[]", []))
    while style.endswith(",default"):
        style = style.removesuffix(",default")
    layout = utils.urls.arg(request.args, "default", "layout")
    return await preview_image(id, style, lines, layout)
