import asyncio

from sanic import Sanic, response
from sanic_ext import openapi

from app import config, helpers, settings, utils

app = Sanic(name="memegen")
config.init(app)


@app.get("/")
@openapi.exclude(True)
def index(request):
    return response.redirect("/docs")


@app.get("/test")
@openapi.exclude(True)
async def test(request):
    if not settings.DEBUG:
        return response.redirect("/")

    urls = await asyncio.to_thread(helpers.get_test_images, request)
    content = utils.html.gallery(urls, columns=False, refresh=20)
    return response.html(content)


@app.get("/favicon.ico")
@openapi.exclude(True)
async def favicon(request):
    return await response.file("app/static/favicon.ico")


@app.get("/robots.txt")
@openapi.exclude(True)
async def robots(request):
    return await response.file("app/static/robots.txt")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        auto_reload=settings.DEBUG,
        access_log=False,
        motd=False,
        fast=True,
    )
