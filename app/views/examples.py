import asyncio
import random

from sanic import Blueprint, response
from sanic.request import Request
from sanic_ext import openapi

from .. import helpers, settings, utils

blueprint = Blueprint("examples", url_prefix="/examples")


@blueprint.get("/")
@openapi.exclude(True)
async def examples(request: Request):
    items = await asyncio.to_thread(helpers.get_example_images, request)
    return display(request, items)


@blueprint.get("/animated")
@openapi.exclude(True)
async def examples_animated(request: Request):
    items = await asyncio.to_thread(helpers.get_example_images, request, animated=True)
    return display(request, items)


@blueprint.get("/static")
@openapi.exclude(True)
async def examples_static(request: Request):
    items = await asyncio.to_thread(helpers.get_example_images, request, animated=False)
    return display(request, items)


def display(request, items):
    urls = [items[0] for items in items]
    if settings.DEBUG:
        refresh = int(request.args.get("refresh", 5 * 60))
    else:
        refresh = 0
        random.shuffle(urls)
    content = utils.html.gallery(urls, columns=True, refresh=refresh)
    return response.html(content)
