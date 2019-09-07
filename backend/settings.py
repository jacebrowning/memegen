import os

if "DOMAIN" in os.environ:
    SITE_DOMAIN = os.environ["DOMAIN"]
    IMAGES_URL = f"https://{SITE_DOMAIN}"
elif "HEROKU_APP_NAME" in os.environ:
    SITE_DOMAIN = os.environ["HEROKU_APP_NAME"] + ".herokuapp.com"
    IMAGES_URL = f"https://{SITE_DOMAIN}"
else:
    SITE_DOMAIN = "localhost:5001"
    IMAGES_URL = "https://memegen-link-v2.herokuapp.com"


PORT = int(os.environ.get("PORT", 8000))
WORKERS = int(os.environ.get("WEB_CONCURRENCY", 1))
DEBUG = bool(os.environ.get("DEBUG", False))
