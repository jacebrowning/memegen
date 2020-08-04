from sanic_openapi import doc as _decorator
from sanic_openapi import swagger_blueprint as blueprint

blueprint.name = "docs"
blueprint.url_prefix = "/api/docs"

exclude = _decorator.exclude(True)
