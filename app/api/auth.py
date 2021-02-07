from sanic import Blueprint, response
from sanic_openapi import doc

from .. import utils

blueprint = Blueprint("Authentication", url_prefix="/auth")


@blueprint.get("/")
@doc.summary("Validate your API key")
@doc.response(200, str, description="Your API key is valid")
@doc.response(401, str, description="Your API key is invalid")
async def validate(request):
    return (
        response.json({"message": "Your API key is valid"}, status=200)
        if utils.meta.authenticated(request)
        else response.json({"message": "Your API key is invalid."}, status=401)
    )
