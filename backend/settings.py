import os

if "DOMAIN" in os.environ:  # staging / production
    SITE_DOMAIN = os.environ["DOMAIN"]
    IMAGES_URL = f"https://{SITE_DOMAIN}"
    API_SCHEMES = ["https"]
elif "HEROKU_APP_NAME" in os.environ:  # review apps
    SITE_DOMAIN = os.environ["HEROKU_APP_NAME"] + ".herokuapp.com"
    IMAGES_URL = f"https://{SITE_DOMAIN}"
    API_SCHEMES = ["https"]
else:  # localhost
    SITE_DOMAIN = "localhost:5001"
    IMAGES_URL = "https://memegen-link-v2.herokuapp.com"
    API_SCHEMES = ["http", "https"]


PORT = int(os.environ.get("PORT", 8000))
WORKERS = int(os.environ.get("WEB_CONCURRENCY", 1))
DEBUG = bool(os.environ.get("DEBUG", False))
