from unittest.mock import Mock

import pytest


class TestImageService:

    def test_find_template(self, image_service):
        mock_template = Mock()
        image_service.template_store.read.return_value = mock_template

        template = image_service.find_template('my_key')

        assert image_service.template_store.read.called

        assert template is mock_template

    def test_find_template_not_found(self, image_service):
        image_service.template_store.read.return_value = None

        with pytest.raises(KeyError):
            image_service.find_template('unknown_key')
