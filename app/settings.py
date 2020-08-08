import os
from pathlib import Path

DEBUG = bool(os.environ.get("DEBUG", False))
ROOT = Path(__file__).parent.parent.resolve()

# Server configuration

PORT = int(os.environ.get("PORT", 5000))
WORKERS = int(os.environ.get("WEB_CONCURRENCY", 1))


if "DOMAIN" in os.environ:  # staging / production
    SERVER_NAME = os.environ["DOMAIN"]
    IMAGES_URL = f"https://{SERVER_NAME}"
    API_SCHEMES = ["https"]
elif "HEROKU_APP_NAME" in os.environ:  # review apps
    SERVER_NAME = os.environ["HEROKU_APP_NAME"] + ".herokuapp.com"
    IMAGES_URL = f"https://{SERVER_NAME}"
    API_SCHEMES = ["https"]
else:  # localhost
    SERVER_NAME = f"localhost:{PORT}"
    IMAGES_URL = "https://memegen-link-v2.herokuapp.com"
    API_SCHEMES = ["http", "https"]


# Fonts

FONTS_DIRECTORY = ROOT / "fonts"
FONT = FONTS_DIRECTORY / "TitilliumWeb-Black.ttf"

# Image rendering

IMAGES_DIRECTORY = ROOT / "images"
DEFAULT_EXT = "png"
DEFAULT_SIZE = (600, 600)

# Test images

TEST_IMAGES_DIRECTORY = ROOT / "app" / "tests" / "images"
TEST_IMAGES = [
    ("iw", ["TESTS CODE", "IN PRODUCTION"]),
    ("fry", ["A", "B"]),
    ("fry", ["SHORT LINE", "LONGER LINE OF TEXT THAN THE SHORT ONE"]),
    ("fry", ["LONGER LINE OF TEXT THAN THE SHORT ONE", "SHORT LINE"]),
    ("sparta", ["", "THIS IS A WIDE IMAGE!"]),
    (
        "ski",
        [
            "IF YOU TRY TO PUT A BUNCH MORE TEXT THAN CAN POSSIBLY FIT ON A MEME",
            "YOU'RE GONNA HAVE A BAD TIME",
        ],
    ),
    ("ds", ["PUSH THIS BUTTON", "OR THIS BUTTON", "CAN'T DECIDE WHICH IS WORSE"]),
]
