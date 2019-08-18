import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
from datafiles import converters, datafile
from jinja2 import Template as JinjaTemplate
from sanic import Sanic, response
from sanic.exceptions import abort
from sanic_openapi import doc, swagger_blueprint

from backend.models import Template

app = Sanic(strict_slashes=True)
app.blueprint(swagger_blueprint)

if "DOMAIN" in os.environ:
    app.config.SERVER_NAME = os.environ["DOMAIN"]
elif "HEROKU_APP_NAME" in os.environ:
    app.config.SERVER_NAME = os.environ["HEROKU_APP_NAME"] + ".herokuapp.com"
else:
    app.config.SERVER_NAME = f'localhost:{os.environ["BACKEND_PORT"]}'

custom = Template("_custom")
error = Template("_error")


@app.get("/")
async def index(request):
    index_path = Path("frontend", "build", "index.html").resolve()
    index_file = await aiofiles.open(index_path)
    template = JinjaTemplate(await index_file.read())
    html = template.render(domain=app.config.SERVER_NAME)
    return response.html(html)


@app.get("/static/<filename:path>")
async def static(request, filename):
    return await response.file(f"frontend/build/static/{filename}")


@app.get("/api/")
async def api(request):
    return response.json(
        {
            "templates": app.url_for("templates", _external=True),
            "images": app.url_for("images", _external=True),
        }
    )


@app.get("/api/templates")
async def templates(request):
    templates = Template.objects.filter(valid=True)
    return response.json([t.json(app) for t in templates])


@app.get("/api/templates/<key>")
async def templates_detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.jsonify(app))
    abort(404)


@app.get("/api/images")
async def images(request):
    templates = Template.objects.filter(valid=True)
    return response.json([{"url": t.build_sample_url(app)} for t in templates])


@app.post("/api/images")
@doc.consumes(doc.JsonBody({"key": str, "lines": [str]}), location="body")
async def create_image(request):
    url = app.url_for(
        "image_text",
        key=request.json["key"],
        lines="/".join(request.json["lines"]),
        _external=True,
    )
    return response.json({"url": url}, status=201)


@app.get("/api/images/<key>.jpg")
async def image_blank(request, key):
    template = Template.objects.get_or_none(key) or error
    path = await template.render("_")
    return await response.file(path)


@app.get("/api/images/<key>/<lines:path>.jpg")
async def image_text(request, key, lines):
    template = Template.objects.get_or_none(key) or error
    path = await template.render(*lines.split("/"))
    return await response.file(path)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=int(os.environ.get("WEB_CONCURRENCY", 1)),
        debug=bool(os.environ.get("DEBUG", False)),
    )
