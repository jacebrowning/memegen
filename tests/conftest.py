# pylint: disable=redefined-outer-name

import pytest

from memegen.factory import create_app
from memegen.settings import get_config

from memegen.tests.conftest import pytest_configure  # pylint: disable=unused-import


# TODO: replace all calls with the new signature
def load(*args, **kwargs):
    from .utils import load
    return load(*args, **kwargs)[1]


@pytest.yield_fixture(scope='session')
def app():
    app = create_app(get_config('test'))
    yield app


@pytest.yield_fixture
def client(app):  # pylint: disable=unused-argument
    yield app.test_client()
