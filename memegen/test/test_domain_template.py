# pylint: disable=unused-variable
# pylint: disable=expression-not-assigned
# pylint: disable=misplaced-comparison-constant

from unittest.mock import patch, Mock

import pytest
from expecter import expect

from memegen.domain import Template


def describe_template():

    def it_supports_comparison():
        t1 = Template('abc', "A Thing")
        t2 = Template('def')
        t3 = Template('def', "Do This")

        assert t1 != t2
        assert t2 == t3
        assert t1 < t3

    def describe_get_path():

        @patch('os.path.isfile', Mock(return_value=True))
        def it_returns_default_when_no_style(template):
            expect(template.get_path()) == "abc/default.png"

        @patch('os.path.isfile', Mock(return_value=True))
        def it_returns_alternate_when_style_provided(template):
            expect(template.get_path('Custom')) == "abc/custom.png"

        @patch('os.path.isfile', Mock(return_value=True))
        def it_returns_default_when_style_is_none(template):
            expect(template.get_path(None)) == "abc/default.png"

    def describe_path():

        def is_returned_when_file_exists(template):
            template.root = "my_root"

            with patch('os.path.isfile', Mock(return_value=True)):
                path = template.path

            assert "my_root/abc/default.png" == path

        def is_none_when_no_file(template):
            template.root = "my_root"

            with patch('os.path.isfile', Mock(return_value=False)):
                path = template.path

            assert None is path

    def describe_default_path():

        def is_based_on_lines(template):
            assert "foo/bar" == template.default_path

        def is_underscore_when_no_lines(template):
            template.lines = []

            assert "_" == template.default_path

    def describe_sample_path():

        def is_based_on_lines(template):
            assert "foo/bar" == template.sample_path

        def is_placeholder_when_no_lines(template):
            template.lines = []

            assert "your-text/goes-here" == template.sample_path

    def describe_validate_meta():

        def with_no_name(template):
            template.name = None

            assert False is template.validate_meta()

        def with_no_default_image(template):
            assert False is template.validate_meta()

        def with_nonalphanumberic_name(template):
            template.name = "'ABC' Meme"

            assert False is template.validate_meta()

    def describe_validate_link():

        def with_bad_link(template):
            mock_response = Mock()
            mock_response.status_code = 404

            with patch('requests.get', Mock(return_value=mock_response)):
                template.link = "example.com/fake"

                assert False is template.validate_link()

        @patch('os.path.isfile', Mock(return_value=True))
        def with_cached_valid_link(template):
            template.link = "example.com"

            assert True is template.validate_link()

    def describe_validate_size():

        @pytest.mark.parametrize('dimensions,valid', [
            ((Template.MIN_WIDTH, Template.MIN_HEIGHT), True),
            ((Template.MIN_WIDTH - 1, Template.MIN_HEIGHT), False),
            ((Template.MIN_WIDTH, Template.MIN_HEIGHT - 1), False),
            ((Template.MIN_WIDTH - 1, Template.MIN_HEIGHT - 1), False),
        ])
        @patch('PIL.Image.open')
        def with_various_dimenions(mock_open, template, dimensions, valid):
            mock_img = Mock()
            mock_img.size = dimensions
            mock_open.return_value = mock_img

            assert valid is template.validate_size()

    def describe_validate():

        def with_no_validators(template):
            assert True is template.validate(validators=[])

        def with_all_passing_validators(template):
            """Verify a template is valid if all validators pass."""
            mock_validators = [lambda: True]

            assert True is template.validate(validators=mock_validators)

        def with_one_failing_validator(template):
            """Verify a template is invalid if any validators fail."""
            mock_validators = [lambda: False]

            assert False is template.validate(validators=mock_validators)
