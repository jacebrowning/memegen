import log
from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint

from app import settings
from app.api.images import blueprint as api_images
from app.api.templates import blueprint as api_templates

app = Sanic(name="memegen")

app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "0.0"
app.config.API_TITLE = "Memes API"


app.blueprint(api_images)
app.blueprint(api_templates)
app.blueprint(swagger_blueprint)


@app.get("/api/")
@doc.exclude(True)
async def api(request):
    return response.json(
        {
            "templates": request.app.url_for("templates.index", _external=True),
            "images": request.app.url_for("images.index", _external=True),
        }
    )


@app.get("/templates/<filename:path>")
@doc.exclude(True)
async def image(request, filename):
    return await response.file(f"templates/{filename}")


@app.get("/debug")
@doc.exclude(True)
async def debug(request):
    return await response.file(f"app/tests/images/index.html")


if __name__ == "__main__":
    log.silence("datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
    )
