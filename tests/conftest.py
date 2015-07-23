# pylint: disable=redefined-outer-name

import json
import logging

import pytest

from memegen.app import create_app
from memegen.settings import get_config

from memegen.test.conftest import pytest_configure  # pylint: disable=unused-import


def load(response, as_json=True, key=None):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')
    if not as_json:
        return text
    if text:
        data = json.loads(text)
        if key:
            data = data[key]
    else:
        data = None
    logging.debug("response: %r", data)
    return data


@pytest.fixture
def app():
    return create_app(get_config('test'))


@pytest.fixture
def client(app):
    return app.test_client()
