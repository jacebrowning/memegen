# pylint: disable=R,C

from memegen import app
from memegen import settings


class TestCreateApp:

    def test_dev(self):
        dev_app = app.create_app(settings.DevConfig)
        assert True is dev_app.config['DEBUG']
