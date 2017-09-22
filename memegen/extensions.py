import os

from flask_cors import CORS
from flask_caching import Cache
from flask_cachecontrol import FlaskCacheControl

cors = CORS()
cache = Cache(config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'data/cache/flask',
    # Heroku will cycle the filesystem every 24 hours and on every deploy
    'CACHE_DEFAULT_TIMEOUT': 60 if os.getenv('FLASK_ENV') == 'dev' else 99999,
})
cache_control = FlaskCacheControl()
