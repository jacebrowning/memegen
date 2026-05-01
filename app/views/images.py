import asyncio

from sanic import Blueprint, exceptions, response
from sanic.log import logger
from sanic.request import Request
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

blueprint = Blueprint("Images", url_prefix="/images")


@blueprint.get("/")
@openapi.summary("List example memes")
@openapi.parameter(
    "filter", str, "query", description="Part of the template name or example to match"
)
@openapi.response(
    200,
    {"application/json": list[ExampleResponse]},
    "Successfully returned a list of example memes",
)
async def index(request: Request):
    query = request.args.get("filter", "").lower()
    examples = await asyncio.to_thread(helpers.get_example_images, request, query)
    return response.json(
        [{"url": url, "template": template} for url, template in examples]
    )


@blueprint.post("/")
@openapi.summary("Create a meme from a template")
@openapi.description(
    "Create a meme by `POST`ing raw text. The response includes a `url` "
    "field containing the canonical, escape-encoded URL — agents that don't "
    "want to implement the escape table client-side should use this endpoint "
    "and read back the URL rather than constructing one themselves.\n\n"
    "Body fields:\n"
    "- `template_id`: ID of the template to render (from `GET /templates/`).\n"
    "- `text`: Lines of text in order (raw, not escape-encoded). Up to the "
    "template's `lines` value; pass an empty string for an empty intermediate "
    "line.\n"
    "- `style`: One or more style names from the template's `styles` array, "
    "or HTTPS URLs to use as custom overlay images. For templates with "
    "`overlays > 1`, the array sets each slot independently.\n"
    "- `extension`: Output format — `png`, `jpg`, `gif`, or `webp`.\n"
    "- `redirect`: If true, returns 302 to the canonical URL instead of "
    "returning JSON."
)
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
async def create(request: Request):
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
async def create_automatic(request: Request):
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
    generator = results[0]["generator"]
    confidence = results[0]["confidence"]
    logger.info(f"Top result: {url} ({generator=} {confidence=})")
    url, _updated = await utils.meta.tokenize(request, url)

    if payload.get("redirect", False):
        return response.redirect(utils.urls.add(url, status="201"))

    return response.json(
        {"url": url, "generator": generator, "confidence": confidence},
        status=201,
    )


@blueprint.post("/custom")
@openapi.summary("Create a meme from any image")
@openapi.body({"application/json": CustomRequest})
@openapi.response(
    201,
    {"application/json": MemeResponse},
    description="Successfully created a meme from a custom image",
)
async def create_custom(request: Request):
    return await generate_url(request)


@blueprint.get("/custom")
@openapi.summary("List popular custom memes")
@openapi.parameter("safe", bool, "query", description="Exclude NSFW results")
@openapi.parameter(
    "filter", str, "query", description="Part of the meme's text to match"
)
@openapi.response(
    200,
    {"application/json": list[MemeResponse]},
    "Successfully returned a list of custom memes",
)
async def index_custom(request: Request):
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


@blueprint.get(r"/<template_filename:.+\.\w+>")
@openapi.summary("Display a template background")
@openapi.parameter(
    "template_filename",
    str,
    "path",
    description=(
        "Template ID and image format: `<template_id>.<extension>`. This is "
        "the canonical empty-template render and matches the `blank` field on "
        "`GET /templates/{id}`. Use this when a client just wants the "
        "background. The same query parameters as "
        "`/images/{template_id}/{text_filepath}` apply."
    ),
)
@openapi.parameter(
    "style",
    str,
    "query",
    description=(
        "Alternate visual variant from the template's `styles` array, OR an "
        "HTTPS URL to use as a custom overlay image. For templates with "
        "`overlays > 1`, may be repeated to set each slot independently. "
        "Unknown style names return HTTP 422, not the default render."
    ),
)
@openapi.parameter(
    "font",
    str,
    "query",
    description=(
        "Font name or alias overriding the template's default. Full list at "
        "`/fonts/`. Named aliases: `thick`, `comic`, `he`, `jp`. Unknown "
        "values return HTTP 422; the image still renders with the template's "
        "default font."
    ),
)
@openapi.parameter(
    "layout",
    str,
    "query",
    description=(
        "`default` (implicit) or `top`. `top` places all text at the image "
        "top rather than the template's default regions."
    ),
)
@openapi.parameter(
    "width",
    int,
    "query",
    description=(
        "Output width in pixels. If both `width` and `height` are supplied, "
        "the image is padded to fit while preserving aspect ratio. Values "
        "between 1 and 9 are rejected with HTTP 422."
    ),
)
@openapi.parameter(
    "height",
    int,
    "query",
    description="Output height in pixels. See `width` for combined behavior.",
)
@openapi.parameter(
    "color",
    str,
    "query",
    description=(
        "Comma-separated `<text>,<outline>` pair. Each value is either an "
        "HTML color name or a hex code (with or without a leading `#`). "
        "Example: `white,black`."
    ),
)
@openapi.parameter(
    "background",
    str,
    "query",
    description=("Custom background image URL. Composes with `style=<url>` overlays."),
)
@openapi.parameter(
    "center",
    str,
    "query",
    description=(
        "Comma-separated `<x>,<y>` fractional coordinates (0.0–1.0) for "
        "overlay center within its slot. Most useful with `style=<url>`."
    ),
)
@openapi.parameter(
    "scale",
    float,
    "query",
    description=(
        "Multiplier applied to the overlay's default size. Most useful with "
        "`style=<url>`."
    ),
)
@openapi.parameter(
    "frames",
    int,
    "query",
    description=(
        "Maximum number of frames to render in animated output (`gif`/"
        "`webp`). 0 (default) means no cap. Use this to bound response size "
        "and render time on long animations."
    ),
)
@openapi.parameter(
    "status",
    int,
    "query",
    description=(
        "Override the HTTP response status code. Primarily used internally "
        "by the `POST /images/` → redirect flow to propagate a `201 Created` "
        "semantic to the final image fetch. Most clients should not need to "
        "set this directly."
    ),
)
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
async def detail_blank(request: Request, template_filename: str):
    template_id, extension = template_filename.rsplit(".", 1)

    if (
        request.args.get("style") == "animated"
        and extension not in settings.ANIMATED_EXTENSIONS
    ):
        # TODO: Move this pattern to utils
        params = {k: v for k, v in request.args.items() if k != "style"}
        url = request.app.url_for(
            "Images.detail_blank",
            template_filename=template_id + ".gif",
            **params,
        )
        return response.redirect(utils.urls.clean(url), status=301)

    return await render_image(request, template_id, extension=extension)


@blueprint.get(r"/<template_id:slug>/<text_filepath:[^/].*\.\w+>")
@openapi.summary("Display a custom meme")
@openapi.parameter(
    "text_filepath",
    str,
    "path",
    description=(
        "Lines of text and image format: `<line1>/<line2>/.../<line_n>."
        "<extension>`, where `n` ≤ the template's `lines` value. Trailing "
        "lines may be omitted; pass `_` (single underscore) for an empty "
        "intermediate line. Extensions: `png`, `jpg`, `gif`, `webp`. Special "
        "characters in each segment use an ASCII-safe escape table: `_` "
        "(space), `__` (literal underscore), `~n` (newline), `~q` (?), `~a` "
        "(&), `~p` (%), `~h` (#), `~s` (/), `~b` (\\), `~l` (<), `~g` (>), "
        "`''` (double quote). Emoji shortcodes (e.g. `:thumbsup:`) are "
        "substituted automatically. Clients that don't want to implement the "
        "escape table should `POST` to `/images/` with raw text in the JSON "
        "body and use the canonical `url` field from the response."
    ),
)
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.parameter(
    "style",
    str,
    "query",
    description=(
        "Alternate visual variant from the template's `styles` array, OR an "
        "HTTPS URL to use as a custom overlay image. For templates with "
        "`overlays > 1`, may be repeated to set each slot independently. "
        "Unknown style names return HTTP 422, not the default render."
    ),
)
@openapi.parameter(
    "font",
    str,
    "query",
    description=(
        "Font name or alias overriding the template's default. Full list at "
        "`/fonts/`. Named aliases: `thick`, `comic`, `he`, `jp`. Unknown "
        "values return HTTP 422; the image still renders with the template's "
        "default font."
    ),
)
@openapi.parameter(
    "layout",
    str,
    "query",
    description=(
        "`default` (implicit) or `top`. `top` places all text at the image "
        "top rather than the template's default regions."
    ),
)
@openapi.parameter(
    "width",
    int,
    "query",
    description=(
        "Output width in pixels. If both `width` and `height` are supplied, "
        "the image is padded to fit while preserving aspect ratio. Values "
        "between 1 and 9 are rejected with HTTP 422."
    ),
)
@openapi.parameter(
    "height",
    int,
    "query",
    description="Output height in pixels. See `width` for combined behavior.",
)
@openapi.parameter(
    "color",
    str,
    "query",
    description=(
        "Comma-separated `<text>,<outline>` pair. Each value is either an "
        "HTML color name or a hex code (with or without a leading `#`). "
        "Example: `white,black`."
    ),
)
@openapi.parameter(
    "background",
    str,
    "query",
    description=("Custom background image URL. Composes with `style=<url>` overlays."),
)
@openapi.parameter(
    "center",
    str,
    "query",
    description=(
        "Comma-separated `<x>,<y>` fractional coordinates (0.0–1.0) for "
        "overlay center within its slot. Most useful with `style=<url>`."
    ),
)
@openapi.parameter(
    "scale",
    float,
    "query",
    description=(
        "Multiplier applied to the overlay's default size. Most useful with "
        "`style=<url>`."
    ),
)
@openapi.parameter(
    "frames",
    int,
    "query",
    description=(
        "Maximum number of frames to render in animated output (`gif`/"
        "`webp`). 0 (default) means no cap. Use this to bound response size "
        "and render time on long animations."
    ),
)
@openapi.parameter(
    "status",
    int,
    "query",
    description=(
        "Override the HTTP response status code. Primarily used internally "
        "by the `POST /images/` → redirect flow to propagate a `201 Created` "
        "semantic to the final image fetch. Most clients should not need to "
        "set this directly."
    ),
)
@openapi.response(200, {"image/*": bytes}, "Successfully displayed a custom meme")
@openapi.response(404, {"image/*": bytes}, "Template not found")
@openapi.response(414, {"image/*": bytes}, "Custom text too long (length >200)")
@openapi.response(415, {"image/*": bytes}, "Unable to download image URL")
@openapi.response(
    422,
    {"image/*": bytes},
    "Invalid style for template or no image URL specified for custom template",
)
async def detail_text(request: Request, template_id: str, text_filepath: str):
    text_paths, extension = text_filepath.rsplit(".", 1)

    if (
        request.args.get("style") == "animated"
        and extension not in settings.ANIMATED_EXTENSIONS
    ):
        # TODO: Move this pattern to utils
        params = {k: v for k, v in request.args.items() if k != "style"}
        url = request.app.url_for(
            "Images.detail_text",
            template_id=template_id,
            text_filepath=text_paths + ".gif",
            **params,
        )
        return response.redirect(utils.urls.clean(url), status=301)

    slug, updated = utils.text.normalize(text_paths)
    if updated:
        url = request.app.url_for(
            "Images.detail_text",
            template_id=template_id,
            text_filepath=slug + "." + extension,
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
            "Images.detail_text",
            template_id=template_id,
            text_filepath=slug + "." + extension,
            **params,
        )
        return response.redirect(utils.urls.clean(url), status=302)

    return await render_image(request, template_id, slug, watermark, extension)
