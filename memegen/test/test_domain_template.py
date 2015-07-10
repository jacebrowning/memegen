# pylint: disable=R,C,W0621

from unittest.mock import patch, Mock

import pytest

from memegen.domain import Template


@pytest.fixture
def template():
    return Template('abc', lines=['foo', 'bar'])


class TestTemplate:

    def test_comparison(self):
        t1 = Template('abc', "A Thing")
        t2 = Template('def')
        t3 = Template('def', "Do This")
        assert t1 != t2
        assert t2 == t3
        assert t1 < t3

    def test_path(self):
        template = Template('abc', root="my_root")
        with patch('os.path.isfile', Mock(return_value=True)):
            path = template.path
        assert "my_root/abc/default.png" == path

    def test_path_is_none_with_no_file(self):
        template = Template('abc', root="my_root")
        with patch('os.path.isfile', Mock(return_value=False)):
            path = template.path
        assert path is None

    def test_default(self, template):
        assert "foo/bar" == template.default

    def test_default_with_no_lines(self):
        template = Template('abc', lines=[])
        assert "" == template.default

    def test_validate_with_no_name(self):
        template = Template('abc')
        assert False is template.validate()

    def test_validate_with_no_default_image(self):
        template = Template('abc', name="ABC")
        assert False is template.validate()

    def test_validate_with_nonalphanumberic_name(self):
        template = Template('abc', name="'ABC' Meme")
        assert False is template.validate()

    def test_validate_with_bad_link(self, template):
        mock_response = Mock()
        mock_response.status_code = 404
        with patch('requests.get', Mock(return_value=mock_response)):
            template.link = "example.com/fake"
            assert False is template.validate()
