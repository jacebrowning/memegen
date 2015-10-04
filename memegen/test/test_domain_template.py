# pylint: disable=no-self-use

from unittest.mock import patch, Mock

import pytest

from memegen.domain import Template


class TestTemplate:

    def test_comparison(self):
        t1 = Template('abc', "A Thing")
        t2 = Template('def')
        t3 = Template('def', "Do This")

        assert t1 != t2
        assert t2 == t3
        assert t1 < t3

    def test_path(self, template):
        template.root = "my_root"

        with patch('os.path.isfile', Mock(return_value=True)):
            path = template.path

        assert "my_root/abc/default.png" == path

    def test_path_is_none_with_no_file(self, template):
        template.root = "my_root"

        with patch('os.path.isfile', Mock(return_value=False)):
            path = template.path

        assert None is path

    def test_default_path(self, template):
        assert "foo/bar" == template.default_path

    def test_default_path_with_no_lines(self, template):
        template.lines = []

        assert "_" == template.default_path

    def test_sample_path(self, template):
        assert "foo/bar" == template.sample_path

    def test_sample_path_with_no_lines(self, template):
        template.lines = []

        assert "your-text/goes-here" == template.sample_path

    def test_validate_meta_with_no_name(self, template):
        template.name = None

        assert False is template.validate_meta()

    def test_validate_meta_with_no_default_image(self, template):
        assert False is template.validate_meta()

    def test_validate_meta_with_nonalphanumberic_name(self, template):
        template.name = "'ABC' Meme"

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
        """Verify a template is valid if all validators pass."""
        mock_validators = [lambda: True]

        assert True is template.validate(validators=mock_validators)

    def test_validate_fail(self, template):
        """Verify a template is invalid if any validators fail."""
        mock_validators = [lambda: False]

        assert False is template.validate(validators=mock_validators)

    @patch('os.path.isfile', Mock(return_value=True))
    def test_validate_link(self, template):
        template.link = "example.com"

        assert True is template.validate_link()

    @pytest.mark.parametrize('dimensions,valid', [
        ((Template.MIN_WIDTH, Template.MIN_HEIGHT), True),
        ((Template.MIN_WIDTH - 1, Template.MIN_HEIGHT), False),
        ((Template.MIN_WIDTH, Template.MIN_HEIGHT - 1), False),
        ((Template.MIN_WIDTH - 1, Template.MIN_HEIGHT - 1), False),
    ])
    @patch('PIL.Image.open')
    def test_validate_size(self, mock_open, template, dimensions, valid):
        mock_img = Mock()
        mock_img.size = dimensions
        mock_open.return_value = mock_img

        assert valid is template.validate_size()
