# pylint: disable=unused-variable,expression-not-assigned,misplaced-comparison-constant,singleton-comparison

from pathlib import Path

import pytest
from expecter import expect

from memegen.domain import Font


def describe_font():

    @pytest.fixture
    def font():
        return Font(Path('mock_dir', 'FooBar.otf'))

    def describe_str():

        def is_based_on_name(font):
            expect(str(font)) == 'foobar'

    def describe_bool():

        def is_based_on_default(font):
            expect(bool(font)) == True

            font.DEFAULT = 'foobar'
            expect(bool(font)) == False

    def describe_name():

        def is_derived_from_filename(font):
            expect(font.name) == 'foobar'

        def it_replaces_underscores(font):
            font.path = Path('a_b')
            expect(font.name) == 'a-b'
