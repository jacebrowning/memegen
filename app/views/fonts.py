from sanic import Blueprint, exceptions, response
from sanic.request import Request
from sanic_ext import openapi

from .. import models
from .schemas import FontResponse

blueprint = Blueprint("Fonts", url_prefix="/fonts")


@blueprint.get("/")
@openapi.summary("List available fonts")
@openapi.response(
    200,
    {"application/json": list[FontResponse]},
    "Successfully returned a list of fonts",
)
async def index(request: Request):
    fonts = models.Font.objects.all()
    data = [font.jsonify(request) for font in fonts]
    return response.json(data)


@blueprint.get("/<id:slug>")
@openapi.summary("View a specific font")
@openapi.parameter("id", str, "path", description="ID of a font")
@openapi.response(
    200,
    {"application/json": FontResponse},
    "Successfully returned a specific font",
)
@openapi.response(404, str, description="Font not found")
async def detail(request, id):
    try:
        font = models.Font.objects.get(id)
    except ValueError:
        raise exceptions.NotFound(f"Template not found: {id}")
    else:
        data = font.jsonify(request)
        return response.json(data)
