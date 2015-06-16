import pytest


class TestImageService:

    def test_find_template_not_found(self, image_service):
        image_service.template_store.read.return_value = None

        with pytest.raises(KeyError):
            image_service.find_template("unknown")
