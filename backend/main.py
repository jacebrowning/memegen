import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from datafiles import converters, datafile
from sanic import Sanic, response
from sanic.exceptions import abort
from sanic_openapi import doc, swagger_blueprint

from backend.models import Template

app = Sanic(strict_slashes=True)
app.blueprint(swagger_blueprint)
app.config.SERVER_NAME = os.getenv("DOMAIN", "localhost:8000")


custom = Template("_custom")
error = Template("_error")


@app.get("/")
async def index(request):
    return response.json(
        {
            "templates": app.url_for("templates", _external=True),
            "images": app.url_for("images", _external=True),
            "_docs": app.url_for("swagger.index", _external=True),
        }
    )


@app.get("/templates")
async def templates(request):
    templates = Template.objects.filter(valid=True)
    return response.json([t.json(app) for t in templates])


@app.get("/templates/<key>")
async def templates_detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.jsonify(app))
    abort(404)


@app.get("/images")
async def images(request):
    templates = Template.objects.filter(valid=True)
    return response.json([{"url": t.build_sample_url(app)} for t in templates])


@app.post("/images")
@doc.consumes(doc.JsonBody({"key": str, "lines": [str]}), location="body")
async def create_image(request):
    url = app.url_for(
        "image_text",
        key=request.json["key"],
        lines="/".join(request.json["lines"]),
        _external=True,
    )
    return response.json({"url": url}, status=201)


@app.get("/images/<key>.jpg")
async def image_blank(request, key):
    template = Template.objects.get_or_none(key) or error
    path = template.render("_")
    return await response.file(path)


@app.get("/images/<key>/<lines:path>.jpg")
async def image_text(request, key, lines):
    template = Template.objects.get_or_none(key) or error
    path = template.render(lines.split("/"))
    return await response.file(path)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=int(os.environ.get("WEB_CONCURRENCY", 1)),
        debug=bool(os.environ.get("DEBUG", False)),
    )
