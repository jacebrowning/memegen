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

    def test_create_image(self, image_service):
        mock_template = Mock()
        mock_text = Mock()
        mock_image = Mock()
        mock_image.template = mock_template
        mock_image.text = mock_text

        image = image_service.create_image(mock_template, mock_text)

        assert image_service.image_store.create.called_once_with(mock_image)

        assert image.template is mock_image.template
        assert image.text is mock_image.text
