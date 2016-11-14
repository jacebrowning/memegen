# pylint: disable=unused-variable,expression-not-assigned,misplaced-comparison-constant,singleton-comparison

import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
from expecter import expect

from memegen.domain import Template


def temp(path):
    return Path(tempfile.gettempdir(), path)


def describe_template():

    def it_supports_comparison():
        t1 = Template('abc', "A Thing")
        t2 = Template('def')
        t3 = Template('def', "Do This")

        assert t1 != t2
        assert t2 == t3
        assert t1 < t3

    def describe_get_path():

        @patch('pathlib.Path.is_file', Mock(return_value=True))
        def it_returns_default_when_no_style(template):
            expect(template.get_path()) == Path("abc/default.png")

        @patch('pathlib.Path.is_file', Mock(return_value=True))
        def it_returns_alternate_when_style_provided(template):
            expect(template.get_path('Custom')) == Path("abc/custom.png")

        @patch('pathlib.Path.is_file', Mock(return_value=True))
        def it_returns_default_when_style_is_none(template):
            expect(template.get_path(None)) == Path("abc/default.png")

        @patch('pathlib.Path.is_file', Mock(return_value=False))
        def it_considers_urls_valid_styles(template):
            url = "http://example.com"
            path = temp("a9b9f04336ce0181a08e774e01113b31")
            expect(template.get_path(url)) == path

        @patch('pathlib.Path.is_file', Mock(return_value=True))
        def it_caches_file_downloads(template):
            url = "http://this/will/be/ignored"
            path = temp("d888710f0697650eb68fc9dcbb976d4c")
            expect(template.get_path(url)) == path

        def it_handles_bad_urls(template):
            expect(template.get_path("http://invalid")) == None

        def it_handles_invalid_paths(template):
            expect(template.get_path("@#$%^")) == None

    def describe_path():

        def is_returned_when_file_exists(template):
            template.root = "my_root"

            with patch('pathlib.Path.is_file', Mock(return_value=True)):
                path = template.path

            expect(path) == Path("my_root/abc/default.png")

        def is_none_when_no_file(template):
            template.root = "my_root"

            with patch('pathlib.Path.is_file', Mock(return_value=False)):
                path = template.path

            expect(path) == None

    def describe_default_path():

        def is_based_on_lines(template):
            expect(template.default_path) == "foo/bar"

        def is_underscore_when_no_lines(template):
            template.lines = []

            expect(template.default_path) == "_"

    def describe_styles():

        @patch('os.listdir', Mock(return_value=[]))
        def is_empty_when_no_alternate_images(template):
            expect(template.styles) == []

        @patch('os.listdir', Mock(return_value=['foo.jpg', 'bar.png']))
        def is_filesnames_of_alternate_images(template):
            expect(template.styles) == ['bar', 'foo']

    def describe_sample_path():

        def is_based_on_lines(template):
            expect(template.sample_path) == "foo/bar"

        def is_placeholder_when_no_lines(template):
            template.lines = []

            expect(template.sample_path) == "your-text/goes-here"

    def describe_keywords():

        def is_the_set_of_all_relevant_terms(template):
            template.lines[0] = "A day in the life"

            expect(template.keywords) == {'abc', 'day', 'the', 'bar', 'life'}

    def describe_match():

        def it_returns_none_when_no_match(template):
            expect(template.match("")) == (0, None)

        def it_returns_the_best_matching_result(template):
            template.compile_regexes([r"(\w*)/?(abc)", r"(\w*)/?(def)"])

            expect(template.match("_/def")) == (0.42, "_/def")

    def describe_search():

        def it_counts_contained_terms(template):
            template.key = 'Foo'
            template.name = "The Foobar Meme"
            template.aliases.append('Foo')
            template.aliases.append('Foobar')
            template.lines[0] = "This on time foobar happened"

            expect(template.search("Foo")) == 5

        def it_treats_none_specially(template):
            expect(template.search(None)) == -1

    def describe_validate_meta():

        def with_no_name(template):
            template.name = None

            expect(template.validate_meta()) == False

        def with_no_default_image(template):
            expect(template.validate_meta()) == False

        def with_nonalphanumberic_name(template):
            template.name = "'ABC' Meme"

            expect(template.validate_meta()) == False

    def describe_validate_link():

        def with_bad_link(template):
            mock_response = Mock()
            mock_response.status_code = 404

            with patch('requests.head', Mock(return_value=mock_response)):
                template.link = "example.com/fake"

                expect(template.validate_link()) == False

        @patch('pathlib.Path.is_file', Mock(return_value=True))
        def with_cached_valid_link(template):
            template.link = "already_cached_site.com"

            expect(template.validate_link()) == True

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

            expect(template.validate_size()) == valid

    def describe_validate_regexes():

        def with_missing_split(template):
            template.compile_regexes([".*"])

            expect(template.validate_regexes()) == False

    def describe_validate():

        def with_no_validators(template):
            expect(template.validate([])) == True

        def with_all_passing_validators(template):
            """Verify a template is valid if all validators pass."""
            mock_validators = [lambda: True]

            expect(template.validate(validators=mock_validators)) == True

        def with_one_failing_validator(template):
            """Verify a template is invalid if any validators fail."""
            mock_validators = [lambda: False]

            expect(template.validate(validators=mock_validators)) == False
