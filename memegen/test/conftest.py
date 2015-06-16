from unittest.mock import Mock

import pytest

from memegen import services


@pytest.fixture
def link_service():
    return services.link.LinkService(template_store=Mock())


@pytest.fixture
def image_service():
    return services.image.ImageService(template_store=Mock(),
                                       image_store=Mock())
