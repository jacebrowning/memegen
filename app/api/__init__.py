from sanic import Blueprint, response

from . import docs, images, legacy_images, templates

blueprint = Blueprint("root", url_prefix="/api")


@blueprint.get("/")
@docs.exclude
async def index(request):
    return response.json(
        {
            "templates": request.app.url_for("templates.index", _external=True),
            "images": request.app.url_for("images.index", _external=True),
            "docs": request.app.url_for("docs.index", _external=True),
        }
    )
