# pylint: disable=unused-variable,expression-not-assigned

from unittest.mock import patch, call, Mock

import pytest
from expecter import expect

from memegen.app import create_app
from memegen.settings import get_config
from memegen.routes._common import display


def describe_display():

    @pytest.fixture
    def app():
        app = create_app(get_config('test'))
        app.config['GOOGLE_ANALYTICS_TID'] = 'my_tid'
        return app

    request_html = Mock(path="it's a path")
    request_html.headers.get = Mock(return_value="text/html")

    request_image = Mock(path="it's a path")
    request_image.headers.get = Mock(return_value="(not a browser)")

    @patch('memegen.routes._common.request', request_html)
    def it_returns_html_for_browsers(app):

        with app.test_request_context():
            html = display("my_title", "my_path", raw=True)

        print(html)
        assert "<title>my_title</title>" in html
        assert 'url("it\'s a path")' in html
        assert "ga('create', 'my_tid', 'auto');" in html

    @patch('memegen.routes._common._track')
    @patch('memegen.routes._common.send_file')
    @patch('memegen.routes._common.request', request_image)
    def it_returns_an_image_otherwise(mock_send_file, mock_track):

        display("my_title", "my_path")

        expect(mock_track.mock_calls) == [
            call("my_title"),
        ]
        expect(mock_send_file.mock_calls) == [
            call("my_path", mimetype='image/jpeg'),
        ]
