from sanic import Blueprint, exceptions, response
from sanic.log import logger
from sanic_openapi import doc

from .. import models, settings, utils

blueprint = Blueprint("Shortcuts", url_prefix="/")


@blueprint.get(r"/images/<template_id:[^.]+>")
@doc.summary("Redirect to an example image")
@doc.consumes(doc.String(name="template_id"), location="path")
@doc.response(
    302, doc.File(), description="Successfully redirected to an example image"
)
@doc.response(404, str, description="Template not found")
@doc.response(501, str, description="Template not fully implemented")
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
@doc.exclude(settings.DEPLOYED)
@doc.summary("Redirect to an example image" + settings.SUFFIX)
@doc.consumes(doc.String(name="template_id"), location="path")
@doc.response(
    302, doc.File(), description="Successfully redirected to an example image"
)
@doc.response(404, str, description="Template not found")
async def legacy_example_image(request, template_id):
    template_id, extension = template_id.rsplit(".", 1)
    template = models.Template.objects.get_or_none(template_id)
    if template:
        url = template.build_example_url(request, extension=extension, external=False)
        return response.redirect(url)
    raise exceptions.NotFound(f"Template not found: {template_id}")


@blueprint.get(r"/<template_id:slug>")
@doc.exclude(settings.DEPLOYED)
@doc.summary("Redirect to an example image" + settings.SUFFIX)
@doc.consumes(doc.String(name="template_id"), location="path")
@doc.response(
    302, doc.File(), description="Successfully redirected to an example image"
)
async def legacy_example_path(request, template_id):
    template_id = template_id.strip("/")
    return response.redirect(f"/images/{template_id}")


@blueprint.get(r"/images/<template_id:slug>/<text_paths:[^/].*>")
@doc.summary("Redirect to a custom image")
@doc.consumes(doc.String(name="text_paths"), location="path")
@doc.consumes(doc.String(name="template_id"), location="path")
@doc.produces(
    str,
    description="Successfully displayed a custom meme",
    content_type="text/html",
)
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
async def custom_path(request, template_id, text_paths):
    if template_id == "images":
        return response.redirect(f"/images/{text_paths}".removesuffix("/"))

    if not settings.DEBUG:
        url = request.app.url_for(
            "Memes.text",
            template_id=template_id,
            text_paths=utils.urls.clean(text_paths) + "." + settings.DEFAULT_EXTENSION,
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
@doc.exclude(settings.DEPLOYED)
@doc.summary("Redirect to a custom image" + settings.SUFFIX)
@doc.consumes(doc.String(name="text_paths"), location="path")
@doc.consumes(doc.String(name="template_id"), location="path")
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
@doc.response(404, str, description="Template not found")
async def legacy_custom_image(request, template_id, text_paths):
    text_paths, extension = text_paths.rsplit(".", 1)
    template = models.Template.objects.get_or_none(template_id)
    if template:
        url = request.app.url_for(
            "Memes.text",
            template_id=template_id,
            text_paths=text_paths + "." + extension,
        )
        return response.redirect(url)
    raise exceptions.NotFound(f"Template not found: {template_id}")


@blueprint.get(r"/<template_id:(?!templates)[a-z-]+>/<text_paths:[^/].*>")
@doc.exclude(settings.DEPLOYED)
@doc.summary("Redirect to a custom image" + settings.SUFFIX)
@doc.consumes(doc.String(name="text_paths"), location="path")
@doc.consumes(doc.String(name="template_id"), location="path")
@doc.response(302, doc.File(), description="Successfully redirected to a custom image")
async def legacy_custom_path(request, template_id, text_paths):
    if template_id == "images":
        return response.redirect(f"/images/{text_paths}".removesuffix("/"))
    return response.redirect(f"/images/{template_id}/{text_paths}")
