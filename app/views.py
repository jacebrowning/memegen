import asyncio

import log
from sanic import Sanic, response

from app import api, helpers, settings, utils

app = Sanic(name="memegen")

app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "6.0a1"
app.config.API_TITLE = "Memes API"


app.blueprint(api.images.blueprint)
app.blueprint(api.templates.blueprint)
app.blueprint(api.docs.blueprint)


@app.get("/")
@api.docs.exclude
async def index(request):
    loop = asyncio.get_event_loop()
    urls = await loop.run_in_executor(None, helpers.get_sample_images, request)
    refresh = "debug" in request.args and settings.DEBUG
    content = utils.html.gallery(urls, refresh=refresh)
    return response.html(content)


@app.get("/test")
@api.docs.exclude
async def test(request):
    if settings.DEBUG:
        loop = asyncio.get_event_loop()
        urls = await loop.run_in_executor(None, helpers.get_test_images, request)
        content = utils.html.gallery(urls, refresh=True)
        return response.html(content)
    return response.redirect("/")


if __name__ == "__main__":
    log.silence("asyncio", "datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        access_log=False,
    )
