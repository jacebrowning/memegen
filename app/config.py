import bugsnag
from aiohttp.client_exceptions import ClientPayloadError
from PIL import UnidentifiedImageError
from sanic.exceptions import MethodNotSupported, NotFound
from sanic.handlers import ErrorHandler

from . import settings, utils, views

IGNORED_EXCEPTIONS = (
    ClientPayloadError,
    MethodNotSupported,
    NotFound,
    UnidentifiedImageError,
)


class BugsnagErrorHandler(ErrorHandler):
    def default(self, request, exception):
        if self._should_notify(exception):
            bugsnag.notify(exception, metadata={"request": request.url})
        return super().default(request, exception)

    @staticmethod
    def _should_notify(exception) -> bool:
        if not settings.BUGSNAG_API_KEY:
            return False
        if isinstance(exception, IGNORED_EXCEPTIONS):
            return False
        return True


def init(app):
    app.config.API_HOST = app.config.SERVER_NAME = settings.SERVER_NAME
    app.config.API_SCHEMES = [settings.SCHEME]
    app.config.API_VERSION = utils.meta.version()
    app.config.API_TITLE = "Memegen.link"
    app.config.API_CONTACT_EMAIL = "support@maketested.com"
    app.config.API_LICENSE_NAME = "View the license"
    app.config.API_LICENSE_URL = (
        "https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt"
    )

    app.config.OAS_UI_DEFAULT = "swagger"
    app.config.SWAGGER_UI_CONFIGURATION = {
        "operationsSorter": "alpha",
        "docExpansion": "list",
    }

    app.ext.openapi.add_security_scheme("ApiKeyAuth", type="apiKey", name="X-API-KEY")
    app.ext.openapi.secured("ApiKeyAuth")

    app.blueprint(views.clients.blueprint)
    app.blueprint(views.memes.blueprint)
    app.blueprint(views.templates.blueprint)
    app.blueprint(views.shortcuts.blueprint)  # registered last to avoid collisions

    app.error_handler = BugsnagErrorHandler()
    bugsnag.configure(
        api_key=settings.BUGSNAG_API_KEY,
        project_root="/app",
        release_stage=settings.RELEASE_STAGE,
    )
