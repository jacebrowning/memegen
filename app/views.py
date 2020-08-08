import log
from sanic import Sanic, response

from app import api, settings, utils
from app.api.images import get_sample_images, get_test_images

app = Sanic(name="memegen")

app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "0.0"
app.config.API_TITLE = "Memes API"

app.blueprint(api.blueprint)
app.blueprint(api.images.blueprint)
app.blueprint(api.legacy_images.blueprint)
app.blueprint(api.templates.blueprint)
app.blueprint(api.docs.blueprint)


@app.get("/")
@api.docs.exclude
def index(request):
    urls = get_sample_images(request)
    refresh = "debug" in request.args and settings.DEBUG
    content = utils.html.gallery(urls, refresh=refresh)
    return response.html(content)


@app.get("/test")
@api.docs.exclude
def test(request):
    if settings.DEBUG:
        urls = get_test_images(request)
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
    )
