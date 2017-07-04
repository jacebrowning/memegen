import os

from . import __project__


class Config:
    """Base configuration."""

    ENV = None

    PATH = os.path.abspath(os.path.dirname(__file__))
    ROOT = os.path.dirname(PATH)
    DEBUG = False
    THREADED = False

    # Constants
    GITHUB_SLUG = "jacebrowning/memegen"
    GITHUB_URL = "https://github.com/{}".format(GITHUB_SLUG)
    GITHUB_BASE = "https://raw.githubusercontent.com/{}/master/".format(GITHUB_SLUG)
    CONTRIBUTING_URL = GITHUB_BASE + "CONTRIBUTING.md"
    CHANGES_URL = GITHUB_BASE + "CHANGELOG.md"

    # Variables
    FACEBOOK_APP_ID = 'localhost'
    FACEBOOK_IMAGE_HEIGHT = os.getenv('FACEBOOK_IMAGE_HEIGHT', 402)
    FACEBOOK_IMAGE_WIDTH = os.getenv('FACEBOOK_IMAGE_WIDTH', 802)
    GOOGLE_ANALYTICS_URL = "http://www.google-analytics.com/collect"
    GOOGLE_ANALYTICS_TID = 'localhost'
    REGENERATE_IMAGES = os.getenv('REGENERATE_IMAGES')
    REMOTE_TRACKING_URL = os.getenv('REMOTE_TRACKING_URL')
    TWITTER_IMAGE_HEIGHT = os.getenv('TWITTER_IMAGE_HEIGHT', 401)
    TWITTER_IMAGE_WIDTH = os.getenv('TWITTER_IMAGE_WIDTH', 801)
    WATERMARK_OPTIONS = os.getenv('WATERMARK_OPTIONS', "").split(',')


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'

    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    GOOGLE_ANALYTICS_TID = os.getenv('GOOGLE_ANALYTICS_TID')


class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'

    DEBUG = True
    TESTING = True

    WATERMARK_OPTIONS = ['test', '']


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'

    DEBUG = True

    WATERMARK_OPTIONS = ['dev', 'localhost', '127.0.0.1']


def get_config(name):
    assert name, "No configuration specified"

    for config in Config.__subclasses__():
        if config.ENV == name:
            return config

    assert False, "No matching configuration: {}".format(name)
