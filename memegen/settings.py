import os
import logging

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
    CHANGES_URL = GITHUB_BASE + "CHANGELOG.md"
    CONTRIBUTING_URL = GITHUB_BASE + "CONTRIBUTING.md"

    # Variables
    BUGSNAG_API_KEY = os.getenv('BUGSNAG_API_KEY')
    FACEBOOK_APP_ID = 'localhost'
    FACEBOOK_IMAGE_HEIGHT = 492
    FACEBOOK_IMAGE_WIDTH = 940
    GOOGLE_ANALYTICS_TID = 'localhost'
    GOOGLE_ANALYTICS_URL = "http://www.google-analytics.com/collect"
    LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
    REGENERATE_IMAGES = os.getenv('REGENERATE_IMAGES')
    REMOTE_TRACKING_URL = os.getenv('REMOTE_TRACKING_URL')
    TWITTER_IMAGE_HEIGHT = 440
    TWITTER_IMAGE_WIDTH = 880
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

    LOG_LEVEL = logging.DEBUG
    WATERMARK_OPTIONS = ['test', 'memegen.test', 'werkzeug']


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'

    DEBUG = True

    LOG_LEVEL = logging.DEBUG
    WATERMARK_OPTIONS = ['localhost'] + Config.WATERMARK_OPTIONS


def get_config(name):
    assert name, "No configuration specified"

    for config in Config.__subclasses__():
        if config.ENV == name:
            return config

    assert False, "No matching configuration: {}".format(name)
    return None
