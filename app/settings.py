import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()

# Server configuration

PORT = int(os.environ.get("PORT", 5000))
WORKERS = int(os.environ.get("WEB_CONCURRENCY", 1))
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
    SERVER_NAME = f"localhost:{PORT}"
    RELEASE_STAGE = "local"
    SCHEME = "http"

BASE_URL = f"{SCHEME}://{SERVER_NAME}"
DEPLOYED = RELEASE_STAGE != "local" and not DEBUG

# Fonts

FONTS_DIRECTORY = ROOT / "fonts"
FONT_THICK = FONTS_DIRECTORY / "TitilliumWeb-Black.ttf"
FONT_THIN = FONTS_DIRECTORY / "TitilliumWeb-SemiBold.ttf"
FONT_TINY = FONTS_DIRECTORY / "MicroFLF-Bold.ttf"
MINIMUM_FONT_SIZE = 7

# Image rendering

IMAGES_DIRECTORY = ROOT / "images"
DEFAULT_EXT = "png"
DEFAULT_STYLE = "default"
PREVIEW_SIZE = (300, 300)
DEFAULT_SIZE = (600, 600)
MAXIMUM_PIXELS = 1920 * 1080
WATERMARK_HEIGHT = 14

# Test images

TEST_IMAGES_DIRECTORY = ROOT / "app" / "tests" / "images"
TEST_IMAGES = [
    (
        "iw",
        ["tests code", "in production"],
    ),
    (
        "fry",
        ["a", "b"],
    ),
    (
        "fry",
        ["short line", "longer line of text than the short one"],
    ),
    (
        "fry",
        ["longer line of text than the short one", "short line"],
    ),
    (
        "sparta",
        ["", "this is a wide image!"],
    ),
    (
        "ski",
        [
            "if you try to put a bunch more text than can possibly fit on a meme",
            "you're gonna have a bad time",
        ],
    ),
    (
        "ds",
        ["Push this button.", "Push that button.", "can't decide which is worse"],
    ),
    (
        "spongebob",
        ["You: Stop talking like that", "Me: Stop talking like that"],
    ),
]

# Analytics

API_KEYS = os.getenv("API_KEYS", "").split(",")

ALLOWED_WATERMARKS = os.getenv("WATERMARK_OPTIONS", ",").split(",")
DISABLED_WATERMARK = ALLOWED_WATERMARKS.pop(0)
DEFAULT_WATERMARK = ALLOWED_WATERMARKS[0]

REMOTE_TRACKING_URL = os.getenv("REMOTE_TRACKING_URL")

BUGSNAG_API_KEY = os.getenv("BUGSNAG_API_KEY")
