import asyncio
import random

import log
from sanic import Sanic, response
from sanic_openapi import doc

from app import config, helpers, settings, utils

app = Sanic(name="memegen")
config.init(app)


@app.get("/")
@doc.exclude(True)
def index(request):
    return response.redirect(request.app.url_for("swagger.index"))


@app.get("/examples")
@doc.exclude(True)
async def examples(request):
    animated = utils.urls.flag(request, "animated")
    items = await asyncio.to_thread(helpers.get_example_images, request, "", animated)
    urls = [items[0] for items in items]
    if settings.DEBUG:
        refresh = int(request.args.get("refresh", 5 * 60))
    else:
        refresh = 0
        random.shuffle(urls)
    content = utils.html.gallery(urls, columns=True, refresh=refresh)
    return response.html(content)


@app.get("/test")
@doc.exclude(True)
async def test(request):
    if not settings.DEBUG:
        return response.redirect("/")

    urls = await asyncio.to_thread(helpers.get_test_images, request)
    content = utils.html.gallery(urls, columns=False, refresh=20)
    return response.html(content)


@app.get("/favicon.ico")
@doc.exclude(True)
async def favicon(request):
    return await response.file("app/static/favicon.ico")


@app.get("/robots.txt")
@doc.exclude(True)
async def robots(request):
    return await response.file("app/static/robots.txt")


if __name__ == "__main__":
    log.reset()
    log.silence("datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        access_log=False,
        motd=False,
    )
