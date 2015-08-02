# pylint: disable=R,C,W0621

from unittest.mock import patch, Mock

import pytest

from memegen.domain import Template


@pytest.fixture
def template():
    return Template('abc', name='ABC', lines=['foo', 'bar'])


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

    def test_validate_meta_with_no_name(self):
        template = Template('abc')
        assert False is template.validate_meta()

    def test_validate_meta_with_no_default_image(self):
        template = Template('abc', name="ABC")
        assert False is template.validate_meta()

    def test_validate_meta_with_nonalphanumberic_name(self):
        template = Template('abc', name="'ABC' Meme")
        assert False is template.validate_meta()

    def test_validate_link_with_bad_link(self, template):
        mock_response = Mock()
        mock_response.status_code = 404
        with patch('requests.get', Mock(return_value=mock_response)):
            template.link = "example.com/fake"
            assert False is template.validate_link()

    def test_validate_pass(self, template):
        assert True is template.validate(validators=[])

    def test_validate_all_pass(self, template):
        """If no validators find issues, the template is considered valid"""
        mock_validators = [
            lambda: True,
        ]

        assert True is template.validate(validators=mock_validators)

    def test_validate_fail(self, template):
        """If any validators find an issue, the template is considered invalid"""
        mock_validators = [
            lambda: False,
        ]

        assert False is template.validate(validators=mock_validators)

    @patch('os.path.isfile', Mock(return_value=True))
    def test_validate_link(self):
        template = Template(key='abc',
                            name="The ABC Meme",
                            link="example.com")

        assert True is template.validate_link()

    @pytest.mark.parametrize('dimensions,valid', [
        ((Template.MIN_WIDTH, Template.MIN_HEIGHT), True),
        ((Template.MIN_WIDTH - 1, Template.MIN_HEIGHT), False),
        ((Template.MIN_WIDTH, Template.MIN_HEIGHT - 1), False),
        ((Template.MIN_WIDTH - 1, Template.MIN_HEIGHT - 1), False),
    ])
    @patch('PIL.Image.open')
    def test_validate_size(self, mock_open, dimensions, valid):
        mock_img = Mock()
        mock_img.size = dimensions
        mock_open.return_value = mock_img

        template = Template(key='abc',
                            name="The ABC Meme",
                            link="example.com")

        assert valid is template.validate_size()
