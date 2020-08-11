from sanic_openapi import doc as _decorator
from sanic_openapi import swagger_blueprint as blueprint

blueprint.url_prefix = "/docs"

exclude = _decorator.exclude(True)
