"""Unit tests configuration file."""

from unittest.mock import Mock

import pytest

from memegen import services
from memegen.domain import Template


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False


@pytest.fixture
def template_service():
    return services.template.TemplateService(template_store=Mock())


@pytest.fixture
def link_service():
    return services.link.LinkService(template_store=Mock())


@pytest.fixture
def image_service():
    return services.image.ImageService(
        template_store=Mock(),
        font_store=Mock(),
        image_store=Mock(),
    )


@pytest.fixture
def template():
    return Template('abc', name='ABC', lines=['foo', 'bar'])
