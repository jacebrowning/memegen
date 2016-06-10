# pylint: disable=redefined-outer-name

import pytest
from testing.postgresql import Postgresql
from sqlalchemy.exc import OperationalError

from memegen.app import create_app
from memegen.extensions import db as _db
from memegen.settings import get_config

from memegen.test.conftest import pytest_configure  # pylint: disable=unused-import


# TODO: replace all calls with the new signature
def load(*args, **kwargs):
    from .utilities import load
    return load(*args, **kwargs)[1]


@pytest.yield_fixture(scope='session')
def app():
    app = create_app(get_config('test'))
    yield app


@pytest.yield_fixture(scope='session')
def postgres():
    try:
        import psycopg2
    except ImportError:
        yield None  # PostgreSQL database adapter is unavailable on this system
    else:
        try:
            with Postgresql() as pg:
                yield pg
        except FileNotFoundError:
            yield None  # PostgreSQL is unavailable on this system


@pytest.yield_fixture(scope='module')
def db_engine(app, postgres):
    if postgres:
        app.config['SQLALCHEMY_DATABASE_URI'] = postgres.url()
        _db.app = app

        with app.app_context():
            _db.create_all()

        yield _db

        # http://stackoverflow.com/a/6810165/1255482
        _db.session.close()  # pylint: disable=no-member

        try:
            _db.drop_all()
        except OperationalError:
            pass  # allow tests to be killed cleanly
    else:
        yield None


@pytest.yield_fixture(scope='function')
def db(db_engine):
    yield db_engine
    # Do a rollback after each test in case bad stuff happened
    if db_engine:
        db_engine.session.rollback()


@pytest.yield_fixture
def client(app, db):  # pylint: disable=unused-argument
    yield app.test_client()
