import asyncio
from typing import List

from sanic import Blueprint, response
from sanic_openapi import doc

from ..helpers import save_image
from ..models import Template


def get_sample_images(request) -> List[str]:
    templates = Template.objects.filter(valid=True)
    return [template.build_sample_url(request.app) for template in templates]


async def render_image(request, key, lines):
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, save_image, key, lines)
    return await response.file(path)


blueprint = Blueprint("images", url_prefix="/api/images")
blueprint_legacy = Blueprint("images-legacy", url_prefix="/")


@blueprint.get("/")
async def index(request):
    urls = get_sample_images(request)
    return response.json([{"url": url} for url in urls])


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
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, save_image, key)
    return await response.file(path)


@blueprint.get("/<key>/<lines:path>.jpg")
async def text(request, key, lines):
    return await render_image(request, key, lines)


@blueprint_legacy.get("/<key>/<lines:path>.jpg")
async def text_legacy(request, key, lines):
    return await render_image(request, key, lines)
