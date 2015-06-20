# pylint: disable=R,C

from unittest.mock import patch, Mock

import pytest

from memegen.domain import Template


class TestTemplateService:

    def test_find_template_not_found(self, template_service):
        template_service.template_store.read.return_value = None

        with pytest.raises(KeyError):
            template_service.find('unknown_key')

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
                              aliases=['123', '456']),
                     Template(key='def',
                              name="The DEF Meme",
                              aliases=['456'])]
        template_service.template_store.filter.return_value = templates

        with patch('os.path.isfile', Mock(return_value=True)):
            assert False is template_service.validate()
