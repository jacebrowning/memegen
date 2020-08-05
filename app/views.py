import log
from sanic import Sanic, response

from app import settings
from app.api import docs, images_api, legacy_images_api, templates_api
from app.api.images_api import get_sample_images, get_test_images
from app.helpers import display_images

app = Sanic(name="memegen")

app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "0.0"
app.config.API_TITLE = "Memes API"

app.blueprint(images_api.blueprint)
app.blueprint(legacy_images_api.blueprint)
app.blueprint(templates_api.blueprint)
app.blueprint(docs.blueprint)


@app.get("/")
@docs.exclude
def index(request):
    urls = get_sample_images(request)
    refresh = "debug" in request.args and settings.DEBUG
    content = display_images(urls, refresh=refresh)
    return response.html(content)


@app.get("/test")
@docs.exclude
def test(request):
    if settings.DEBUG:
        urls = get_test_images(request)
        content = display_images(urls, refresh=True)
        return response.html(content)
    return response.redirect("/")


@app.get("/api/")
@docs.exclude
async def api(request):
    return response.json(
        {
            "templates": request.app.url_for("templates.index", _external=True),
            "images": request.app.url_for("images.index", _external=True),
            "docs": request.app.url_for("docs.index", _external=True),
        }
    )


@app.get("/templates/<filename:path>")
@docs.exclude
async def image(request, filename):
    return await response.file(f"templates/{filename}")


if __name__ == "__main__":
    log.silence("asyncio", "datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
    )
