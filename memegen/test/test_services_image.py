# pylint: disable=no-self-use

from unittest.mock import Mock


class TestImageService:

    mock_template = Mock()
    mock_text = Mock()
    mock_image = Mock()
    mock_image.template = mock_template
    mock_image.text = mock_text

    def test_create(self, image_service):
        image = image_service.create(self.mock_template, self.mock_text)

        assert image_service.image_store.create.called_once_with(
            self.mock_image)

        assert image.template is self.mock_image.template
        assert image.text is self.mock_image.text
