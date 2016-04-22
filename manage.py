#!env/bin/python

import os
import subprocess
import logging

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from memegen.settings import get_config
from memegen.app import create_app


# Select app configuration from the environment
config = get_config(os.getenv('CONFIG', 'dev'))

# Build the app using configuration from the environment
app = create_app(config)

# Populate unset environment variables
for name, command in [
    ('DEPLOY_DATE', "TZ=America/Detroit date '+%F %T'"),
]:
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                            universal_newlines=True).stdout.strip() or "???"
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
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
