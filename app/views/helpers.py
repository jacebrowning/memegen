import asyncio
from contextlib import suppress

from sanic import exceptions, response
from sanic.log import logger
from sanic.request import Request

from .. import models, settings, utils


async def generate_url(
    request: Request,
    template_id: str = "",
    *,
    template_id_required: bool = False,
):
    if request.form:
        payload = dict(request.form)
        for key in list(payload.keys()):
            if "style" not in key and "text" not in key:
                payload[key] = payload.pop(key)[0]
    else:
        try:
            payload = request.json or {}
        except exceptions.InvalidUsage:
            payload = {}

    with suppress(KeyError):
        payload["style"] = payload.pop("style[]")
    with suppress(KeyError):
        payload["text"] = payload.pop("text[]")
    with suppress(KeyError):
        payload["text_lines"] = payload.pop("text_lines[]")

    if template_id_required:
        try:
            template_id = payload["template_id"]
        except KeyError:
            return response.json({"error": '"template_id" is required'}, status=400)
        else:
            template_id = utils.text.slugify(template_id)

    style: str = utils.urls.arg(payload, "", "style", "overlay")
    if isinstance(style, list):
        style = ",".join([(s.strip() or "default") for s in style])
    while style.endswith(",default"):
        style = style.removesuffix(",default")
    text_lines = utils.urls.arg(payload, [], "text", "text_lines")
    layout = utils.urls.arg(payload, "default", "layout")
    normalize = layout == "default"
    font = utils.urls.arg(payload, "", "font")
    background = utils.urls.arg(payload, "", "background", "image_url")
    extension = utils.urls.arg(payload, "", "extension")

    if (
        background
        and background != settings.PLACEHOLDER
        and not utils.urls.schema(background)
    ):
        logger.info(f"Handling template ID as custom background: {background}")
        template_id = background

    status = 201
    if template_id:
        template: models.Template = models.Template.objects.get_or_create(template_id)
        url = template.build_custom_url(
            request,
            text_lines,
            normalize=normalize,
            style=style,
            layout=layout,
            font=font,
            extension=extension,
        )
        if not template.valid:
            status = 404
            template.delete()
    else:
        template = models.Template("_custom")
        url = template.build_custom_url(
            request,
            text_lines,
            normalize=normalize,
            background=background,
            style=style,
            layout=layout,
            font=font,
            extension=extension,
        )

    url, _updated = await utils.meta.tokenize(request, url)

    logger.info(f"Generated image: {payload} => {url}")

    if payload.get("redirect", False):
        return response.redirect(utils.urls.add(url, status="201"))

    return response.json({"url": url}, status=status)


async def preview_image(request: Request, id: str, style: str, lines: list[str]):
    error = ""

    id = utils.urls.clean(id)
    if utils.urls.schema(id):
        template = await models.Template.create(id)
        if not template.image.exists():
            logger.error(f"Unable to download image URL: {id}")
            template = models.Template.objects.get("_error")
            error = "Invalid Background"
    else:
        template = models.Template.objects.get_or_none(id)
        if not template:
            logger.error(f"No such template: {id}")
            template = models.Template.objects.get("_error")
            error = "Unknown Template"

    if not any(line.strip() for line in lines):
        lines = template.example

    template = await template.clone(request.args, len(lines), style, animated=False)

    if not utils.urls.schema(style):
        style = style.strip().lower()
    if style != "animated" and not await template.check(style):
        error = "Invalid Overlay"

    if error:
        watermark = error
    elif style == "animated" and not template.animated_image:
        watermark = "Animated Text"
    elif style == "default" and template.animated_image:
        watermark = "Static Background"
    else:
        watermark = ""

    data, content_type = await asyncio.to_thread(
        utils.images.preview, template, lines, style=style, watermark=watermark
    )
    return response.raw(data, content_type=content_type)


async def render_image(
    request: Request,
    id: str,
    slug: str = "",
    watermark: str = "",
    extension: str = settings.DEFAULT_STATIC_EXTENSION,
):
    logger.info(f"Rendering image: {request.url}")

    lines = utils.text.decode(slug)
    status = int(utils.urls.arg(request.args, "200", "status"))
    frames = int(request.args.get("frames", 0))
    style = utils.urls.arg(request.args, "default", "style")

    animated = extension in settings.ANIMATED_EXTENSIONS
    if extension not in settings.ALLOWED_EXTENSIONS:
        logger.error(f"Invalid extension: {extension}")
        extension = settings.DEFAULT_STATIC_EXTENSION
        status = 422

    template: models.Template
    if any(len(part.encode()) > 200 for part in slug.split("/")):
        logger.error(f"Slug too long: {slug}")
        slug = slug[:50] + "..."
        lines = utils.text.decode(slug)
        template = models.Template.objects.get("_error")
        style = "default"
        status = 414

    elif id == "custom":
        url = utils.urls.arg(request.args, None, "background")
        if url:
            template = await models.Template.create(url)
            if not template.image.exists():
                logger.error(f"Unable to download image URL: {url}")
                template = models.Template.objects.get("_error")
                if url != settings.PLACEHOLDER:
                    status = 415
        else:
            logger.error("No image URL specified for custom template")
            template = models.Template.objects.get("_error")
            style = "default"
            status = 422
    else:
        template = models.Template.objects.get_or_none(id)
        if not template or not template.image.exists():
            logger.error(f"No such template: {id}")
            template = models.Template.objects.get("_error")
            if id != settings.PLACEHOLDER:
                status = 404

    if status < 400:
        template = await template.clone(
            request.args, len(lines), style, animated=animated
        )
        if not await template.check(style, animated=animated):
            if utils.urls.schema(style):
                status = 415
            elif style != settings.PLACEHOLDER:
                logger.error(f"Invalid style: {style}")
                status = 422

    font_name = utils.urls.arg(request.args, "", "font")
    if font_name == settings.PLACEHOLDER:
        font_name = ""
    else:
        try:
            models.Font.objects.get(font_name)
        except ValueError:
            logger.error(f"Invalid font: {font_name}")
            font_name = ""
            status = 422

    try:
        size = int(request.args.get("width", 0)), int(request.args.get("height", 0))
        if 0 < size[0] < 10 or 0 < size[1] < 10:
            raise ValueError(f"Dimensions are too small: {size}")
    except ValueError as e:
        logger.error(f"Invalid size: {e}")
        size = 0, 0
        status = 422

    if status < 400:
        asyncio.create_task(utils.meta.track(request, lines))

    path = await asyncio.to_thread(
        utils.images.save,
        template,
        lines,
        watermark,
        font_name=font_name,
        extension=extension,
        style=style,
        size=size,
        maximum_frames=frames,
    )
    mime_type = "image/webp" if path.suffix == ".webp" else None
    return await response.file(path, status, mime_type=mime_type)
