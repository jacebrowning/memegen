import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()

PLACEHOLDER = "string"  # Swagger UI placeholder value

# Server configuration

DEBUG = bool(os.environ.get("DEBUG", False))

if "DOMAIN" in os.environ:  # staging / production
    SERVER_NAME = os.environ["DOMAIN"]
    RELEASE_STAGE = "staging" if "staging" in SERVER_NAME else "production"
    SCHEME = "https"
elif "HEROKU_APP_NAME" in os.environ:  # review apps
    SERVER_NAME = os.environ["HEROKU_APP_NAME"] + ".herokuapp.com"
    RELEASE_STAGE = "review"
    SCHEME = "https"
else:  # localhost
    SERVER_NAME = "localhost:5000"
    RELEASE_STAGE = "local"
    SCHEME = "http"

BASE_URL = f"{SCHEME}://{SERVER_NAME}"
DEPLOYED = RELEASE_STAGE != "local" and not DEBUG

# Fonts

DEFAULT_FONT = "thick"

MINIMUM_FONT_SIZE = 7

# Image rendering

IMAGES_DIRECTORY = ROOT / "images"

DEFAULT_STYLE = "default"
DEFAULT_EXTENSION = "png"
ALLOWED_EXTENSIONS = [DEFAULT_EXTENSION, "jpg", "jpeg", "gif", "webp"]
PLACEHOLDER_SUFFIX = ".img"

PREVIEW_SIZE = (300, 300)
DEFAULT_SIZE = (600, 600)

MAXIMUM_PIXELS = 1920 * 1080
MAXIMUM_FRAMES = 20

# Watermarks

DISABLED_WATERMARK = "none"
DEFAULT_WATERMARK = "Memegen.link"
ALLOWED_WATERMARKS = [DEFAULT_WATERMARK]

WATERMARK_HEIGHT = 15

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
]

# Analytics

TRACK_REQUESTS = True
REMOTE_TRACKING_URL = os.getenv("REMOTE_TRACKING_URL")

REMOTE_TRACKING_ERRORS = 0
REMOTE_TRACKING_ERRORS_LIMIT = int(os.getenv("REMOTE_TRACKING_ERRORS_LIMIT", "10"))

BUGSNAG_API_KEY = os.getenv("BUGSNAG_API_KEY")
