from textwrap import dedent

import bugsnag
from aiohttp.client_exceptions import ClientPayloadError
from PIL import UnidentifiedImageError
from sanic import Request, Sanic
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
    def default(self, request: Request, exception):
        if self._should_notify(exception):
            bugsnag.notify(
                exception,
                metadata={
                    "request": {
                        "method": request.method,
                        "url": request.url,
                        "json": request.json,
                        "form": request.form,
                        "headers": request.headers,
                    }
                },
            )
        return super().default(request, exception)

    @staticmethod
    def _should_notify(exception) -> bool:
        if not settings.BUGSNAG_API_KEY:
            return False
        if isinstance(exception, IGNORED_EXCEPTIONS):
            return False
        return True


def init(app: Sanic):
    app.config.SERVER_NAME = settings.BASE_URL
    app.config.CORS_ORIGINS = "*"
    app.config.CORS_SEND_WILDCARD = True
    app.config.OAS_UI_DEFAULT = "swagger"
    app.config.SWAGGER_UI_CONFIGURATION = {
        "apisSorter": "alpha",
        "operationsSorter": "method",
        "docExpansion": "list",
    }

    app.blueprint(views.examples.blueprint)
    app.blueprint(views.clients.blueprint)
    app.blueprint(views.fonts.blueprint)
    app.blueprint(views.images.blueprint)
    app.blueprint(views.templates.blueprint)
    app.blueprint(views.shortcuts.blueprint)

    app.config.MOTD = False
    app.ext._display = lambda: None  # type: ignore

    app.ext.openapi.add_security_scheme("ApiKeyAuth", type="apiKey", name="X-API-KEY")
    app.ext.openapi.secured("ApiKeyAuth")
    app.ext.openapi.describe(
        "Memegen.link",
        version=utils.meta.version(),
        description=dedent("""
        ## Quickstart

        Fetch the list of templates:

        ```
        $ http GET https://api.memegen.link/templates

        [
            {
                "id": "aag",
                "name": "Ancient Aliens Guy",
                "lines": 2,
                "overlays": 0,
                "styles": [],
                "blank": "https://api.memegen.link/images/aag.png",
                "example": {
                    "text": [
                        "",
                        "aliens"
                    ],
                    "url": "https://api.memegen.link/images/aag/_/aliens.png"
                },
                "source": "http://knowyourmeme.com/memes/ancient-aliens",
            },
            ...
        ]
        ```

        Add text to create a meme:

        ```
        $ http POST https://api.memegen.link/images template_id=aag "text[]=foo" "text[]=bar"

        {
            "url": "https://api.memegen.link/images/aag/foo/bar.png"
        }
        ```

        View the image: <https://api.memegen.link/images/aag/foo/bar.png>

        For the full URL-construction reference, see [`docs/guide.md`](https://github.com/jacebrowning/memegen/blob/main/docs/guide.md).

        <details>
        <summary>URL anatomy</summary>

        A rendered meme URL has the form:

        ```
        /images/{template_id}/{line_1}/{line_2}/.../{line_n}.{ext}
        ```

        where `n` is at most the template's `lines` value, and `{ext}` is one of `png`, `jpg`, `gif`, or `webp`. Trailing lines may be omitted; pass `_` to render an empty line in a non-trailing position. The blank template is at `/images/{template_id}.{ext}`.

        The four template-metadata fields that govern URL construction are `id`, `lines`, `overlays`, and `styles`. The remaining fields are descriptive.
        </details>

        <details>
        <summary>Special characters</summary>

        | Character | Escape |
        |-----------|--------|
        | Space | `_` |
        | Underscore | `__` |
        | Newline | `~n` |
        | `?` | `~q` |
        | `&` | `~a` |
        | `%` | `~p` |
        | `#` | `~h` |
        | `/` | `~s` |
        | `\\` | `~b` |
        | `<` | `~l` |
        | `>` | `~g` |
        | `"` | `''` |

        Emoji are supported via shortcode aliases (e.g. `:thumbsup:`). Alternatively, `POST` to `/images/` with raw text and use the canonical `url` field from the response.
        </details>

        <details>
        <summary>Rendering options</summary>

        These query parameters apply to all path-based image endpoints:

        - `style=<name>` — alternate visual variant from the template's `styles` array; also accepts an HTTPS URL for a custom overlay
        - `font=<name>` — override the template's default font; full list at `/fonts/`
        - `layout=top` — place all text at the top
        - `width=<int>`, `height=<int>` — output dimensions in pixels
        - `color=<text>,<outline>` — HTML color names or hex codes
        - `background=<url>` — custom background image
        - `center=<x>,<y>`, `scale=<float>` — overlay placement modifiers (when `overlays > 0`)
        - `frames=<int>` — cap on rendered frames for animated output (`gif`/`webp`); `0` (default) means no cap
        </details>

        ## Links
        """.replace("https://api.memegen.link", settings.BASE_URL)),
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
