from urllib.parse import parse_qs

from sanic import Blueprint, exceptions, response
from sanic.log import logger
from sanic_ext import openapi

from .. import models, settings, utils

blueprint = Blueprint("shortcuts", url_prefix="/")


@blueprint.get(r"/images/<template_id:[^.]+>")
@openapi.summary("Redirect to an example image")
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.response(
    302, {"image/*": bytes}, "Successfully redirected to an example image"
)
@openapi.response(404, {"text/html": str}, "Template not found")
@openapi.response(501, {"text/html": str}, "Template not fully implemented")
async def example_path(request, template_id):
    template_id = utils.urls.clean(template_id)

    if settings.DEBUG:
        template = models.Template.objects.get_or_create(template_id)
    else:
        template = models.Template.objects.get_or_none(template_id)

    if template and template.valid:
        url = template.build_example_url(request, external=False)
        if settings.DEBUG:
            url = url.removesuffix(".png")
        return response.redirect(url)

    if settings.DEBUG:
        if "<" in template_id:
            message = f"Replace {template_id!r} in the URL"
        else:
            message = f"Template not fully implemented: {template}"
            logger.warning(message)
            template.datafile.save()
        raise exceptions.SanicException(message, 501)

    raise exceptions.NotFound(f"Template not found: {template_id}")


@blueprint.get(r"/<template_id:.+\.\w+>")
@openapi.summary("Redirect to an example image")
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.response(
    302, {"image/*": bytes}, "Successfully redirected to an example image"
)
@openapi.response(404, {"text/html": str}, "Template not found")
async def legacy_example_image(request, template_id):
    template_id, extension = template_id.rsplit(".", 1)
    template = models.Template.objects.get_or_none(template_id)
    if template:
        url = template.build_example_url(request, extension=extension, external=False)
        return response.redirect(url)
    raise exceptions.NotFound(f"Template not found: {template_id}")


@blueprint.get("/<template_id:slug>")
@openapi.summary("Redirect to an example image")
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.response(
    302, {"image/*": bytes}, "Successfully redirected to an example image"
)
async def legacy_example_path(request, template_id):
    template_id = template_id.strip("/")
    return response.redirect(f"/images/{template_id}")


@blueprint.get(r"/images/<template_id:slug>/<text_paths:[^/].*>")
@openapi.summary("Redirect to a custom image")
@openapi.parameter(
    "text_paths", str, "path", description="Lines of text: `<line1>/<line2>`"
)
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.response(302, {"image/*": bytes}, "Successfully redirected to a custom image")
async def custom_path(request, template_id, text_paths):
    if template_id == "images":
        return response.redirect(f"/images/{text_paths}".removesuffix("/"))

    params = {}
    text_paths = utils.urls.clean(text_paths)
    if "&" in text_paths:
        logger.warning(f"Fixing query string: {text_paths}")
        text_paths, query_string = text_paths.split("&", 1)
        params = parse_qs(query_string)
    elif "//" in text_paths:
        logger.warning(f"Truncating path: {text_paths}")
        text_paths = text_paths.split("//")[0]
    elif text_paths.endswith("/"):
        logger.warning(f"Fixing trailing slash: {text_paths}")
        text_paths = text_paths.rstrip("/")
    elif text_paths.endswith('"'):
        logger.warning(f"Fixing trailing quote: {text_paths}")
        text_paths = text_paths.rstrip('"')

    if "." in text_paths.strip("."):
        text_filepath = text_paths
    elif text_paths.startswith("."):
        return response.redirect(
            request.app.url_for(
                "images.detail_blank",
                template_filename=f"{template_id}{text_paths}",
            )
        )
    else:
        text_filepath = text_paths + "." + settings.DEFAULT_EXTENSION

    if not settings.DEBUG:
        url = request.app.url_for(
            "images.detail_text",
            template_id=template_id,
            text_filepath=text_filepath,
            **params,
        )
        return response.redirect(url)

    template = models.Template.objects.get_or_create(template_id)
    template.datafile.save()
    animated = utils.urls.flag(request, "animated")
    extension = "gif" if animated else "png"
    content = utils.html.gallery(
        [f"/images/{template_id}/{text_paths}.{extension}"],
        columns=False,
        refresh=30 if animated else 3,
        query_string=request.query_string,
    )
    return response.html(content)


@blueprint.get(r"/<template_id:(?!templates)[a-z-]+>/<text_paths:[^/].*\.\w+>")
@openapi.summary("Redirect to a custom image")
@openapi.parameter(
    "text_paths", str, "path", description="Lines of text: `<line1>/<line2>`"
)
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.response(302, {"image/*": bytes}, "Successfully redirected to a custom image")
@openapi.response(404, {"text/html": str}, description="Template not found")
async def legacy_custom_image(request, template_id, text_paths):
    text_paths, extension = text_paths.rsplit(".", 1)
    template = models.Template.objects.get_or_none(template_id)
    if template:
        url = request.app.url_for(
            "images.detail_text",
            template_id=template_id,
            text_filepath=text_paths + "." + extension,
        )
        return response.redirect(url)
    raise exceptions.NotFound(f"Template not found: {template_id}")


@blueprint.get(r"/<template_id:(?!templates)[a-z-]+>/<text_paths:[^/].*>")
@openapi.summary("Redirect to a custom image")
@openapi.parameter(
    "text_paths", str, "path", description="Lines of text: `<line1>/<line2>`"
)
@openapi.parameter("template_id", str, "path", description="ID of a meme template")
@openapi.response(302, {"image/*": bytes}, "Successfully redirected to a custom image")
async def legacy_custom_path(request, template_id, text_paths):
    if template_id == "images":
        return response.redirect(f"/images/{text_paths}".removesuffix("/"))
    return response.redirect(f"/images/{template_id}/{text_paths}")
