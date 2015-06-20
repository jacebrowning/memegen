#!env/bin/python

import os
import logging

from flask_script import Manager, Server

from memegen.settings import get_config
from memegen.app import create_app


config = get_config(os.getenv('CONFIG'))
app = create_app(config)
manager = Manager(app)


@manager.command
def validate():
    if app.template_service.validate():
        return 0
    else:
        return 1


manager.add_command('server', Server(host='0.0.0.0'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    logging.getLogger('yorm').setLevel(logging.WARNING)
    manager.run()
