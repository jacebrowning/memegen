# pylint: disable=no-self-use

from memegen import app
from memegen import settings


class TestCreateApp:

    def test_prod(self):
        _app = app.create_app(settings.ProdConfig)

        assert False is _app.config['DEBUG']
        assert False is _app.config['TESTING']

    def test_test(self):
        _app = app.create_app(settings.TestConfig)

        assert True is _app.config['DEBUG']
        assert True is _app.config['TESTING']

    def test_dev(self):
        _app = app.create_app(settings.DevConfig)

        assert True is _app.config['DEBUG']
        assert False is _app.config['TESTING']
