# pylint: disable=unused-variable

from unittest.mock import patch, Mock

from memegen.app import create_app
from memegen.settings import get_config
from memegen.routes._common import display


def describe_display():

    app = create_app(get_config('test'))
    app.config['GOOGLE_ANALYTICS_TID'] = 'my_tid'

    request_html = Mock()
    request_html.headers.get = Mock(return_value="text/html")
    request_html.path = "it's a path"

    @patch('memegen.routes._common.request', request_html)
    def it_returns_html_for_browsers():

        with app.test_request_context():
            html = display("my_title", "my_path", raw=True)

        print(html)
        assert "<title>my_title</title>" in html
        assert 'url("it\'s a path")' in html
        assert "ga('create', 'my_tid', 'auto');" in html
