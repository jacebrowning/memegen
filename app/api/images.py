from sanic import Blueprint, response
from sanic_openapi import doc

from ..helpers import save_image
from ..models import Template

blueprint = Blueprint("images", url_prefix="/api/images")


@blueprint.get("/")
async def index(request):
    templates = Template.objects.filter(valid=True)
    return response.json([{"url": t.build_sample_url(request.app)} for t in templates])


@blueprint.post("/")
@doc.consumes(doc.JsonBody({"key": str, "lines": [str]}), location="body")
async def create(request):
    url = request.app.url_for(
        "images.text",
        key=request.json["key"],
        lines="/".join(request.json["lines"]),
        _external=True,
    )
    return response.json({"url": url}, status=201)


@blueprint.get("/<key>.jpg")
async def blank(request, key):
    path = save_image(key)
    return await response.file(path)


@blueprint.get("/<key>/<lines:path>.jpg")
async def text(request, key, lines):
    path = save_image(key, lines)
    return await response.file(path)
