from flask_cors import CORS
from flask_caching import Cache
from flask_cachecontrol import FlaskCacheControl

cors = CORS()
cache = Cache(config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'data/cache/flask',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60,
})
cache_control = FlaskCacheControl()
