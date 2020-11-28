from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic.log import logger
from sanic_openapi import doc

from .. import models, settings, utils

blueprint = Blueprint("shortcuts", url_prefix="/")


@blueprint.get("/images/<template_key>")
@doc.summary("Redirect to a example image")
@doc.response(302, doc.File(), description="Successfully redirected to a example image")
@doc.response(404, str, description="Template not found")
@doc.response(501, str, description="Template not fully implemented")
async def example(request, template_key):
    if settings.DEBUG:
        template = models.Template.objects.get_or_create(template_key)
    else:
        template = models.Template.objects.get_or_none(template_key)

    if template and template.valid:
        url = template.build_example_url(
            request.app, "shortcuts.custom", external=False
        )
        return response.redirect(url)

    if settings.DEBUG:
        if "<" in template_key:
            message = f"Replace {template_key!r} in the URL"
        else:
            message = f"Template not fully implemented: {template}"
            logger.warning(message)
            template.datafile.save()
        abort(501, message)

    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>.png")
@doc.summary("Redirect to a example image")
@doc.exclude(settings.DEPLOYED)
@doc.response(302, doc.File(), description="Successfully redirected to a example image")
@doc.response(404, str, description="Template not found")
async def example_png(request, template_key):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = template.build_example_url(request.app, external=False)
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>.jpg")
@doc.summary("Redirect to a example image")
@doc.exclude(settings.DEPLOYED)
@doc.response(302, doc.File(), description="Successfully redirected to a example image")
@doc.response(404, str, description="Template not found")
async def example_jpg(request, template_key):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = template.build_example_url(request.app, "images.text_jpg", external=False)
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>")
@doc.summary("Redirect to a example image")
@doc.exclude(settings.DEPLOYED)
@doc.response(302, doc.File(), description="Successfully redirected to a example image")
async def example_legacy(request, template_key):
    return response.redirect(f"/images/{template_key}")


@blueprint.get("/images/<template_key>/<text_paths:[\\s\\S]+>")
@doc.summary("Redirect to a custom image")
@doc.produces(
    str,
    description="Successfully displayed a custom meme",
    content_type="text/html",
)
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
async def custom(request, template_key, text_paths):
    if not settings.DEBUG:
        url = request.app.url_for(
            f"images.text_{settings.DEFAULT_EXT}",
            template_key=template_key,
            text_paths=text_paths,
        )
        return response.redirect(url)

    template = models.Template.objects.get_or_create(template_key)
    template.datafile.save()
    url = f"/images/{template_key}/{text_paths}.png"
    content = utils.html.gallery([url], columns=False, refresh=True, rate=1.0)
    return response.html(content)


@blueprint.get("/<template_key>/<text_paths:[\\s\\S]+>.png")
@doc.summary("Redirect to a custom image")
@doc.exclude(settings.DEPLOYED)
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
@doc.response(404, str, description="Template not found")
async def custom_png(request, template_key, text_paths):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = request.app.url_for(
            "images.text_png", template_key=template_key, text_paths=text_paths
        )
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>/<text_paths:[\\s\\S]+>.jpg")
@doc.summary("Redirect to a custom image")
@doc.exclude(settings.DEPLOYED)
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
@doc.response(404, str, description="Template not found")
async def custom_jpg(request, template_key, text_paths):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = request.app.url_for(
            "images.text_jpg", template_key=template_key, text_paths=text_paths
        )
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>/<text_paths:[\\s\\S]+>")
@doc.summary("Redirect to a custom image")
@doc.exclude(settings.DEPLOYED)
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
async def custom_legacy(request, template_key, text_paths):
    return response.redirect(f"/images/{template_key}/{text_paths}")
