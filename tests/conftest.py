# pylint: disable=redefined-outer-name

import json
import logging

import pytest
from testing.postgresql import Postgresql
from sqlalchemy.exc import OperationalError

from memegen.app import create_app
from memegen.extensions import db as _db
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
    logging.debug("Response: %r", data)
    return data


@pytest.yield_fixture(scope='session')
def app(postgres):
    app = create_app(get_config('test'))
    app.config['SQLALCHEMY_DATABASE_URI'] = postgres.url()
    yield app


@pytest.yield_fixture(scope='session')
def postgres():
    with Postgresql() as pg:
        yield pg


@pytest.yield_fixture(scope='module')
def db_engine(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    # http://stackoverflow.com/a/6810165/1255482
    _db.session.close()  # pylint: disable=no-member

    try:
        _db.drop_all()
    except OperationalError:
        # Allow tests to be killed cleanly
        pass


@pytest.yield_fixture(scope='function')
def db(db_engine):
    yield db_engine
    # Do a rollback after each test in case bad stuff happened
    db_engine.session.rollback()


@pytest.yield_fixture
def client(app, db):  # pylint: disable=unused-argument
    yield app.test_client()
