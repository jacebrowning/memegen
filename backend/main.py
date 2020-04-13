from pathlib import Path

import aiofiles
import log
from datafiles import converters, datafile
from sanic import Sanic, response
from sanic.exceptions import abort
from sanic_openapi import doc, swagger_blueprint

from backend import settings
from backend.api.images import blueprint as api_images
from backend.api.templates import blueprint as api_templates
from backend.models import Template

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
async def backend_image(request, filename):
    return await response.file(f"templates/{filename}")


@app.get("/")
@doc.exclude(True)
async def frontend_index(request):
    path = Path("frontend", "build", "index.html").resolve()
    return await response.file(path)


@app.get("/static/<filename:path>")
@doc.exclude(True)
async def frontend_static(request, filename):
    return await response.file(f"frontend/build/static/{filename}")


@app.get("/<filename:path>")
@doc.exclude(True)
async def frontend_public(request, filename):
    return await response.file(f"frontend/build/{filename}")


if __name__ == "__main__":
    log.silence("datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
    )
