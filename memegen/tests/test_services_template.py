# pylint: disable=no-self-use,misplaced-comparison-constant

from unittest.mock import patch, Mock

import pytest

from memegen.domain import Template


@patch('memegen.domain.Template.validate', Mock(return_value=True))
class TestTemplateService:

    def test_find_template_not_found(self, template_service):
        template_service.template_store.read.return_value = None
        template_service.template_store.filter.return_value = []

        with pytest.raises(KeyError):
            template_service.find('unknown_key')

    def test_find_template_allow_missing(self, template_service):
        template_service.template_store.read.return_value = None
        template_service.template_store.filter.return_value = []

        template = template_service.find('unknown_key', allow_missing=True)

        assert 'unknown_key' == template.key
        assert template.get_path().endswith("/static/images/missing.png")

    def test_find_template_by_alias(self, template_service):
        template = Template('hello', aliases=['hello-world', 'helloworld'])
        template_service.template_store.read.return_value = None
        template_service.template_store.filter.return_value = [template]

        template = template_service.find('HELLO_WORLD')

        assert 'hello' == template.key

    def test_aliases(self, template_service):
        template = Template('a', aliases=['b', 'c'])
        template_service.template_store.filter.return_value = [template]

        aliases = template_service.aliases()

        assert ['a', 'b', 'c'] == sorted(aliases)

    def test_aliases_with_filter(self, template_service):
        template = Template('a1', aliases=['a2', 'b1'])
        template_service.template_store.filter.return_value = [template]

        aliases = template_service.aliases('a')

        assert ['a1', 'a2'] == sorted(aliases)

    def test_validate_with_good_templates(self, template_service):
        templates = [Template(key='abc',
                              name="The ABC Meme"),
                     Template(key='def',
                              name="The DEF Meme",
                              aliases=['def2'])]
        template_service.template_store.filter.return_value = templates

        assert True is template_service.validate()

    def test_validate_with_bad_templates(self, template_service):
        mock_template = Mock()
        mock_template.validate.return_value = False
        template_service.template_store.filter.return_value = [mock_template]

        assert False is template_service.validate()

    def test_validate_with_duplicate_aliases(self, template_service):
        templates = [Template(key='abc',
                              name="The ABC Meme",
                              aliases=['123', 'the-meme']),
                     Template(key='def',
                              name="The DEF Meme",
                              aliases=['the-meme'])]
        template_service.template_store.filter.return_value = templates

        assert False is template_service.validate()

    def test_validate_with_misformatted_aliases(self, template_service):
        templates = [Template(key='abc',
                              name="The ABC Meme",
                              aliases=['abc-meme', 'Bad Format'])]
        template_service.template_store.filter.return_value = templates

        assert False is template_service.validate()
