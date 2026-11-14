import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()

PLACEHOLDER = "string"  # Swagger UI placeholder value

# Server configuration

DEBUG = os.environ.get("DEBUG", "false") == "true"

if "BASE_URL" in os.environ:  # explicit public origin (e.g. running in a container)
    # Highest-priority override: declare the exact scheme://host[:port] the
    # service is actually reached on. SERVER_NAME (set from BASE_URL below)
    # drives every absolute URL the app emits -- image / template / font links
    # AND the Swagger UI's openapi.json + swagger-config -- so setting it to the
    # real origin fixes them all when serving on a non-default host, a published
    # port that differs from the internal one, or behind a reverse proxy.
    # Accepts values with or without a scheme, and with or without a trailing /
    # (e.g. "https://api.example.com", "http://localhost:8080", "localhost:8080").
    _origin = os.environ["BASE_URL"].strip().rstrip("/")
    _scheme, _sep, _host = _origin.partition("://")
    SCHEME, SERVER_NAME = (_scheme, _host) if _sep else ("http", _origin)
    RELEASE_STAGE = os.environ.get("RELEASE_STAGE", "production")
elif "DOMAIN" in os.environ:  # staging / production
    SERVER_NAME = os.environ["DOMAIN"]
    RELEASE_STAGE = "staging" if "staging" in SERVER_NAME else "production"
    SCHEME = "https"
elif "HEROKU_APP_NAME" in os.environ:  # review apps
    SERVER_NAME = os.environ["HEROKU_APP_NAME"] + ".herokuapp.com"
    RELEASE_STAGE = "review"
    SCHEME = "https"
else:  # localhost / bare-container default
    # Respect PORT so the default origin matches a container whose internal and
    # published ports are the same (e.g. `run -p 7000:7000` with PORT=7000).
    SERVER_NAME = f"localhost:{os.environ.get('PORT', '5000')}"
    RELEASE_STAGE = "local"
    SCHEME = "http"

BASE_URL = f"{SCHEME}://{SERVER_NAME}"
DEPLOYED = RELEASE_STAGE != "local" and not DEBUG

# Fonts

DEFAULT_FONT = "thick"

MINIMUM_FONT_SIZE = 7

# Image rendering

IMAGES_DIRECTORY = ROOT / "images"

ALLOWED_EXTENSIONS = {"gif", "jpg", "jpeg", "png", "webp"}
ANIMATED_EXTENSIONS = {"gif", "webp"}

DEFAULT_STATIC_EXTENSION = os.environ.get("DEFAULT_STATIC_EXTENSION", "png")
DEFAULT_ANIMATED_EXTENSION = os.environ.get("DEFAULT_ANIMATED_EXTENSION", "gif")

DEFAULT_SUFFIX = "." + DEFAULT_STATIC_EXTENSION
PLACEHOLDER_SUFFIX = ".img"

PREVIEW_SIZE = (300, 300)
DEFAULT_SIZE = (600, 600)

MAXIMUM_PIXELS = 1920 * 1080
MAXIMUM_DOWNLOAD_SIZE = int(os.getenv("MAXIMUM_DOWNLOAD_SIZE", 20 * 1024 * 1024))
MAXIMUM_REDIRECTS = 5
MAXIMUM_FRAMES = 20
MINIMUM_FRAMES = 5

# Watermarks

DISABLED_WATERMARK = "none"
DEFAULT_WATERMARK = "Memegen.link"
ALLOWED_WATERMARKS = [DEFAULT_WATERMARK]

WATERMARK_HEIGHT = 20
WATERMARK_ALPHA = 0.65

PREVIEW_TEXT = "PREVIEW"

# Test images

TEST_IMAGES_DIRECTORY = ROOT / "app" / "tests" / "images"
TEST_IMAGES = [
    (
        "iw",
        ["tests code", "in production"],
        "jpg",
    ),
    (
        "fry",
        ["a", "b"],
        "png",
    ),
    (
        "fry",
        ["short line", "longer line of text than the short one"],
        "png",
    ),
    (
        "fry",
        ["longer line of text than the short one", "short line"],
        "png",
    ),
    (
        "sparta",
        ["", "this is a wide image!"],
        "png",
    ),
    (
        "ski",
        [
            "if you try to put a bunch more text than can possibly fit on a meme",
            "you're gonna have a bad time",
        ],
        "png",
    ),
    (
        "ds",
        ["Push this button.", "Push that button.", "can't decide which is worse"],
        "png",
    ),
    (
        "spongebob",
        ["You: Stop talking like that", "Me: Stop talking like that"],
        "png",
    ),
    (
        "mouth",
        ["Sales Team presenting solution that won't work", "Excited Customer", "Me"],
        "png",
    ),
    (
        "cmm",
        ["Many\nextra\nlines\nof\ntext"],
        "png",
    ),
    (
        "oprah",
        ["you get animated text", "and you get animated text"],
        "gif",
    ),
    (
        "oprah",
        ["you get animated text", "and you get animated text"],
        "webp",
    ),
]

# Analytics

TRACK_REQUESTS = True
REMOTE_TRACKING_URL = os.getenv("REMOTE_TRACKING_URL")

REMOTE_TRACKING_ERRORS = 0
REMOTE_TRACKING_ERRORS_LIMIT = int(os.getenv("REMOTE_TRACKING_ERRORS_LIMIT", "10"))

BUGSNAG_API_KEY = os.getenv("BUGSNAG_API_KEY")
