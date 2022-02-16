from textwrap import dedent

import bugsnag
from aiohttp.client_exceptions import ClientPayloadError
from PIL import UnidentifiedImageError
from sanic import Sanic
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


def init(app: Sanic):
    app.config.SERVER_NAME = settings.SERVER_NAME
    app.config.OAS_UI_DEFAULT = "swagger"
    app.config.SWAGGER_UI_CONFIGURATION = {
        "operationsSorter": "alpha",
        "docExpansion": "list",
    }

    app.blueprint(views.clients.blueprint)
    app.blueprint(views.memes.blueprint)
    app.blueprint(views.templates.blueprint)
    app.blueprint(views.shortcuts.blueprint)

    app.ext.openapi.add_security_scheme("ApiKeyAuth", type="apiKey", name="X-API-KEY")
    app.ext.openapi.secured("ApiKeyAuth")
    app.ext.openapi.describe(
        "Memegen.link",
        version=utils.meta.version(),
        description=dedent(
            """
        ## Quickstart

        Fetch the list of templates:

        ```
        $ http GET https://api.memegen.link/templates

        [
            {
                "_self": "https://api.memegen.link/templates/aag",
                "blank": "https://api.memegen.link/images/aag.png",
                "example": {
                    "text": [
                        "",
                        "aliens"
                    ],
                    "url": "https://api.memegen.link/images/aag/_/aliens.png"
                },
                "id": "aag",
                "lines": 2,
                "name": "Ancient Aliens Guy",
                "overlays": 0,
                "source": "http://knowyourmeme.com/memes/ancient-aliens",
                "styles": []
            },
            ...
        ]
        ```

        Add text to create a meme:

        ```
        $ http POST https://api.memegen.link/images template_id=aag "text_lines[]=foo" "text_lines[]=bar"

        {
            "url": "https://api.memegen.link/images/aag/foo/bar.png"
        }
        ```

        View the image: <https://api.memegen.link/images/aag/foo/bar.png>

        ## Links
        """
        ),
    )
    app.ext.openapi.contact(name="support", email="support@maketested.com")
    app.ext.openapi.license(
        name="View the license",
        url="https://github.com/jacebrowning/memegen/blob/main/LICENSE.txt",
    )

    app.error_handler = BugsnagErrorHandler()
    bugsnag.configure(
        api_key=settings.BUGSNAG_API_KEY,
        project_root="/app",
        release_stage=settings.RELEASE_STAGE,
    )
