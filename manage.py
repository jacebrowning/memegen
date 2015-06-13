#!env/bin/python

import os

from memegen.settings import get_config
from memegen.app import create_app


config = get_config(os.getenv('CONFIG'))
app = create_app(config)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
