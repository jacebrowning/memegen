# pylint: disable=R,C

from unittest.mock import patch, Mock

import pytest

from memegen.domain import Template


class TestTemplateService:

    def test_find_template_not_found(self, template_service):
        template_service.template_store.read.return_value = None
        template_service.template_store.filter.return_value = []

        with pytest.raises(KeyError):
            template_service.find('unknown_key')

    def test_find_template_by_alias(self, template_service):
        template = Template('hello', aliases=['hello-world', 'helloworld'])
        template_service.template_store.read.return_value = None
        template_service.template_store.filter.return_value = [template]

        template = template_service.find('HELLO_WORLD')

        assert 'hello' == template.key

    def test_validate_with_good_templates(self, template_service):
        templates = [Template(key='abc',
                              name="The ABC Meme"),
                     Template(key='def',
                              name="The DEF Meme",
                              aliases=['def2'])]
        template_service.template_store.filter.return_value = templates

        with patch('os.path.isfile', Mock(return_value=True)):
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

        with patch('os.path.isfile', Mock(return_value=True)):
            assert False is template_service.validate()

    def test_validate_with_misformatted_aliases(self, template_service):
        templates = [Template(key='abc',
                              name="The ABC Meme",
                              aliases=['abc-meme', 'Bad Format'])]
        template_service.template_store.filter.return_value = templates

        with patch('os.path.isfile', Mock(return_value=True)):
            assert False is template_service.validate()

    def test_validate_link(self, template_service):
        templates = [Template(key='abc',
                              name="The ABC Meme",
                              link="example.com")]
        template_service.template_store.filter.return_value = templates

        with patch('os.path.isfile', Mock(return_value=True)):
            assert True is template_service.validate()
