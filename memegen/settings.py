import os


class Config:

    """Base configuration."""

    ENV = None

    PATH = os.path.abspath(os.path.dirname(__file__))
    ROOT = os.path.dirname(PATH)
    DEBUG = False
    THREADED = False


class ProdConfig(Config):

    """Production configuration."""

    ENV = 'prod'


class TestConfig(Config):

    """Test configuration."""

    ENV = 'test'

    DEBUG = True
    TESTING = True


class DevConfig(Config):

    """Development configuration."""

    ENV = 'dev'

    DEBUG = True


def get_config(name):
    assert name, "no configuration specified"
    for config in Config.__subclasses__():  # pylint: disable=E1101
        if config.ENV == name:
            return config
    assert False, "no matching configuration"
