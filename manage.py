#!env/bin/python

import os
import logging
from subprocess import check_output

from flask_script import Manager, Server

from memegen.settings import get_config
from memegen.app import create_app


# Select app configuration from the environment
config = get_config(os.getenv('CONFIG'))

# Build the app using configuration from the environment
app = create_app(config)

# Populate unset environment variables
for name, command in [
    ('DEPLOY_DATE', "TZ=America/Detroit date '+%F %T'"),
]:
    output = check_output(command, shell=True, universal_newlines=True).strip()
    os.environ[name] = os.getenv(name, output)

# Configure the command-line interface
manager = Manager(app)


@manager.command
def validate():
    if app.template_service.validate():
        return 0
    else:
        return 1


manager.add_command('server', Server(host='0.0.0.0'))


if __name__ == '__main__':
    manager.run()
