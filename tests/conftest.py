"""Integration tests configuration file."""

import pytest

from memegen.factory import create_app
from memegen.settings import get_config

from memegen.tests.conftest import pytest_configure  # pylint: disable=unused-import


@pytest.yield_fixture(scope='session')
def app():
    yield create_app(get_config('test'))


@pytest.yield_fixture
def client(app):  # pylint: disable=redefined-outer-name
    yield app.test_client()


@pytest.yield_fixture
def public_client(app):  # pylint: disable=redefined-outer-name
    backup = app.config['WATERMARK_OPTIONS']
    app.config['WATERMARK_OPTIONS'] = ['memegen.link']

    yield app.test_client()

    app.config['WATERMARK_OPTIONS'] = backup
