import asyncio

import log
from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint

from app import api, helpers, settings, utils

app = Sanic(name="memegen")
app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "6.0a1"
app.config.API_TITLE = "Memes API"

swagger_blueprint.url_prefix = "/docs"

app.blueprint(api.images.blueprint)
app.blueprint(api.templates.blueprint)
app.blueprint(api.shortcuts.blueprint)
app.blueprint(swagger_blueprint)


@app.get("/")
@doc.exclude(True)
async def index(request):
    return response.redirect("/docs")


@app.get("/samples")
@doc.exclude(True)
async def samples(request):
    loop = asyncio.get_event_loop()
    samples = await loop.run_in_executor(None, helpers.get_sample_images, request)
    urls = [sample[0] for sample in samples]
    refresh = "debug" in request.args and settings.DEBUG
    content = utils.html.gallery(urls, refresh=refresh)
    return response.html(content)


@app.get("/test")
@doc.exclude(True)
async def test(request):
    if not settings.DEBUG:
        return response.redirect("/")
    loop = asyncio.get_event_loop()
    urls = await loop.run_in_executor(None, helpers.get_test_images, request)
    content = utils.html.gallery(urls, refresh=True)
    return response.html(content)


@app.get("/<template_key>")
@doc.tag("shortcuts")
@doc.summary("Redirect to a sample image")
async def legacy_template(request, template_key):
    return response.redirect(f"/images/{template_key}")


if __name__ == "__main__":
    log.silence("asyncio", "datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        access_log=False,
    )
