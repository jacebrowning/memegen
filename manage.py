#!env/bin/python

import os

from flask_script import Manager, Server
from whitenoise import WhiteNoise

from memegen.settings import get_config
from memegen.app import create_app


# Select app configuration from the environment
config = get_config(os.getenv('CONFIG', 'dev'))

# Build the app using configuration from the environment
_app = create_app(config)

# Build the production app with static files support
app = WhiteNoise(_app)
app.add_files("data/images")
app.add_files("memegen/static")


if __name__ == '__main__':
    manager = Manager(_app)

    @manager.command
    def validate():
        if _app.template_service.validate():  # pylint: disable=no-member
            return 0
        else:
            return 1

    server = Server(host='0.0.0.0')
    manager.add_command('server', server)

    manager.run()
