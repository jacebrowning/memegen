from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic_openapi import doc

from .. import models, settings, utils

blueprint = Blueprint("shortcuts", url_prefix="/")


@blueprint.get("/images/<template_key>")
@doc.summary("Redirect to a sample image")
async def sample(request, template_key):
    if settings.DEBUG:
        template = models.Template.objects.get_or_create(template_key)
    else:
        template = models.Template.objects.get_or_none(template_key)

    if template and template.valid:
        url = template.build_sample_url(request.app, "shortcuts.custom", external=False)
        return response.redirect(url)

    if settings.DEBUG:
        template.datafile.save()
        abort(501, f"Template not implemented: {template_key}")

    abort(404, f"Template not found: {template_key}")


@blueprint.get("/images/<template_key>/<text_paths:path>")
@doc.summary("Redirect to a custom image")
async def custom(request, template_key, text_paths):
    if not settings.DEBUG:
        url = request.app.url_for(
            "images.text", template_key=template_key, text_paths=text_paths
        )
        return response.redirect(url)

    template = models.Template.objects.get_or_create(template_key)
    template.datafile.save()
    url = f"/images/{template_key}/{text_paths}.png"
    content = utils.html.gallery([url], refresh=True, rate=1.0)
    return response.html(content)


@blueprint.get("/<template_key>.png")
@doc.summary("Redirect to a sample image")
async def legacy_sample_png(request, template_key):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = template.build_sample_url(request.app, external=False)
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>.jpg")
@doc.summary("Redirect to a sample image")
async def legacy_sample_jpg(request, template_key):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = template.build_sample_url(request.app, "images.text_jpg", external=False)
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>/<text_paths:path>.png")
@doc.summary("Redirect to a sample image")
async def legacy_custom_png(request, template_key, text_paths):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = request.app.url_for(
            "images.text", template_key=template_key, text_paths=text_paths
        )
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")


@blueprint.get("/<template_key>/<text_paths:path>.jpg")
@doc.summary("Redirect to a sample image")
async def legacy_custom_jpg(request, template_key, text_paths):
    template = models.Template.objects.get_or_none(template_key)
    if template:
        url = request.app.url_for(
            "images.text_jpg", template_key=template_key, text_paths=text_paths
        )
        return response.redirect(url)
    abort(404, f"Template not found: {template_key}")
