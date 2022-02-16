import asyncio

from sanic import Blueprint, exceptions, response
from sanic.log import logger
from sanic_ext import openapi

from .. import helpers, settings, utils
from .helpers import render_image
from .schemas import (
    AutomaticRequest,
    CustomRequest,
    ErrorResponse,
    ExampleResponse,
    MemeRequest,
    MemeResponse,
)
from .templates import generate_url

blueprint = Blueprint("Memes", url_prefix="/images")


@blueprint.get("/")
@openapi.summary("List example memes")
@openapi.operation("Memes.list")
@openapi.parameter(
    "filter", str, "query", description="Part of the template name or example to match"
)
@openapi.response(
    200,
    {"application/json": list[ExampleResponse]},
    "Successfully returned a list of example memes",
)
async def index(request):
    query = request.args.get("filter", "").lower()
    examples = await asyncio.to_thread(helpers.get_example_images, request, query)
    return response.json(
        [{"url": url, "template": template} for url, template in examples]
    )


@blueprint.post("/")
@openapi.summary("Create a meme from a template")
@openapi.operation("Memes.create")
@openapi.body({"application/json": MemeRequest})
@openapi.response(
    201, {"application/json": MemeResponse}, "Successfully created a meme"
)
@openapi.response(
    400,
    {"application/json": ErrorResponse},
    'Required "template_id" missing in request body',
)
@openapi.response(
    404, {"application/json": ErrorResponse}, 'Specified "template_id" does not exist'
)
async def create(request):
    return await generate_url(request, template_id_required=True)


@blueprint.post("/automatic")
@openapi.exclude(not settings.REMOTE_TRACKING_URL)
@openapi.summary("Create a meme from word or phrase")
@openapi.body({"application/json": AutomaticRequest})
@openapi.response(
    201, {"application/json": MemeResponse}, "Successfully created a meme"
)
@openapi.response(
    400, {"application/json": ErrorResponse}, 'Required "text" missing in request body'
)
async def automatic(request):
    if request.form:
        payload = dict(request.form)
    else:
        try:
            payload = request.json or {}
        except exceptions.InvalidUsage:
            payload = {}

    try:
        query = payload["text"]
    except KeyError:
        return response.json({"error": '"text" is required'}, status=400)

    results = await utils.meta.search(request, query, payload.get("safe", True))
    logger.info(f"Found {len(results)} result(s)")
    if not results:
        return response.json({"message": f"No results matched: {query}"}, status=404)

    url = utils.urls.normalize(results[0]["image_url"])
    confidence = results[0]["confidence"]
    logger.info(f"Top result: {url} ({confidence})")
    url, _updated = await utils.meta.tokenize(request, url)

    if payload.get("redirect", False):
        return response.redirect(utils.urls.add(url, status="201"))

    return response.json({"url": url, "confidence": confidence}, status=201)


@blueprint.post("/custom")
@openapi.summary("Create a meme from any image")
@openapi.body({"application/json": CustomRequest})
@openapi.response(
    201,
    {"application/json": MemeResponse},
    description="Successfully created a meme from a custom image",
)
async def custom(request):
    return await generate_url(request)


@blueprint.get("/custom")
@openapi.summary("List popular custom memes")
@openapi.operation("Memes.list_custom")
@openapi.parameter("safe", bool, "query", description="Exclude NSFW results")
@openapi.parameter(
    "filter", str, "query", description="Part of the meme's text to match"
)
@openapi.response(
    200,
    {"application/json": list[MemeResponse]},
    "Successfully returned a list of custom memes",
)
async def list_custom(request):
    query = request.args.get("filter", "").lower()
    safe = utils.urls.flag(request, "safe", True)

    results = await utils.meta.search(request, query, safe, mode="results")
    logger.info(f"Found {len(results)} result(s)")
    if not results:
        return response.json({"message": f"No results matched: {query}"}, status=404)

    items = []
    for result in results:
        url = utils.urls.normalize(result["image_url"])
        url, _updated = await utils.meta.tokenize(request, url)
        items.append({"url": url})

    return response.json(items, status=200)


@blueprint.get(r"/<template_id:.+\.\w+>")
@openapi.tag("Templates")
@openapi.summary("Display a template background")
@openapi.parameter("template_id", str, "path")
@openapi.response(
    200, {"image/*": bytes}, "Successfully displayed a template background"
)
@openapi.response(404, {"image/*": bytes}, "Template not found")
@openapi.response(415, {"image/*": bytes}, "Unable to download image URL")
@openapi.response(
    422,
    {"image/*": bytes},
    "Invalid style for template or no image URL specified for custom template",
)
async def blank(request, template_id):
    template_id, extension = template_id.rsplit(".", 1)

    if request.args.get("style") == "animated" and extension != "gif":
        # TODO: Move this pattern to utils
        params = {k: v for k, v in request.args.items() if k != "style"}
        url = request.app.url_for(
            "Memes.blank",
            template_id=template_id + ".gif",
            **params,
        )
        return response.redirect(utils.urls.clean(url), status=301)

    return await render_image(request, template_id, extension=extension)


@blueprint.get(r"/<template_id:slug>/<text_paths:[^/].*\.\w+>")
@openapi.summary("Display a custom meme")
@openapi.parameter("text_paths", str, "path")
@openapi.parameter("template_id", str, "path")
@openapi.response(200, {"image/*": bytes}, "Successfully displayed a custom meme")
@openapi.response(404, {"image/*": bytes}, "Template not found")
@openapi.response(414, {"image/*": bytes}, "Custom text too long (length >200)")
@openapi.response(415, {"image/*": bytes}, "Unable to download image URL")
@openapi.response(
    422,
    {"image/*": bytes},
    "Invalid style for template or no image URL specified for custom template",
)
async def text(request, template_id, text_paths):
    text_paths, extension = text_paths.rsplit(".", 1)

    if request.args.get("style") == "animated" and extension != "gif":
        # TODO: Move this pattern to utils
        params = {k: v for k, v in request.args.items() if k != "style"}
        url = request.app.url_for(
            "Memes.text",
            template_id=template_id,
            text_paths=text_paths + ".gif",
            **params,
        )
        return response.redirect(utils.urls.clean(url), status=301)

    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "Memes.text",
            template_id=template_id,
            text_paths=slug + "." + extension,
            **request.args,
        )
        return response.redirect(utils.urls.clean(url), status=301)

    url, updated = await utils.meta.tokenize(request, request.url)
    if updated:
        return response.redirect(url, status=302)

    watermark, updated = await utils.meta.get_watermark(request)
    if updated:
        # TODO: Move this pattern to utils
        params = {k: v for k, v in request.args.items() if k != "watermark"}
        url = request.app.url_for(
            "Memes.text",
            template_id=template_id,
            text_paths=slug + "." + extension,
            **params,
        )
        return response.redirect(utils.urls.clean(url), status=302)

    return await render_image(request, template_id, slug, watermark, extension)
