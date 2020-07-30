import os

PORT = int(os.environ.get("PORT", 5000))
WORKERS = int(os.environ.get("WEB_CONCURRENCY", 1))
DEBUG = bool(os.environ.get("DEBUG", False))

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
