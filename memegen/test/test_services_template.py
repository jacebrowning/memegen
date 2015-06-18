import pytest


class TestImageService:

    def test_find_template_not_found(self, template_service):
        template_service.template_store.read.return_value = None

        with pytest.raises(KeyError):
            template_service.find('unknown_key')
