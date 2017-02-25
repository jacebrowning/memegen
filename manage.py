#!env/bin/python

import os

from flask_script import Command, Manager, Server

from memegen.settings import get_config
from memegen.factory import create_app


class Validate(Command):
    """Checks for issues in all templates."""

    # pylint: disable=method-hidden

    def run(self):
        if app.template_service.validate():
            return 0
        else:
            return 1


def find_assets():
    """Yield paths for all static files and templates."""
    for name in ['static', 'templates']:
        directory = os.path.join(app.config['PATH'], name)
        for entry in os.scandir(directory):
            if entry.is_file():
                yield entry.path


# Select app configuration from the environment
config = get_config(os.getenv('FLASK_CONFIG', 'dev'))

# Build the app using configuration from the environment
app = create_app(config)

# Configure the command-line interface
manager = Manager(app)
manager.add_command('validate', Validate())
manager.add_command('run', Server(host='0.0.0.0', extra_files=find_assets()))


if __name__ == '__main__':
    manager.run()
