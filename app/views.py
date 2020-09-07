import asyncio

import log
from sanic import Sanic, response
from sanic_openapi import doc

from app import helpers, settings, utils

app = Sanic(name="memegen")
helpers.configure(app)


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


@app.get("/favicon.ico")
async def favicon(request):
    return await response.file("app/static/favicon.ico")


@app.middleware("response")
async def set_cache_control(request, response):
    response.headers["Cache-Control"] = "public, max-age=86400"


if __name__ == "__main__":
    log.reset()
    log.silence("asyncio", "datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        access_log=False,
    )
