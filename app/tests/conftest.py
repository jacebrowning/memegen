import os

import pytest

from ..models import Template
from ..views import app


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False


def pytest_runtest_setup(item):
    for marker in item.iter_markers(name="slow"):
        if "SKIP_SLOW" in os.environ:
            pytest.skip("slow test")


@pytest.fixture
def client():
    return app.test_client


@pytest.fixture
def unknown_template():
    template = Template.objects.get_or_create("unknown")
    template.delete()
    yield template
    template.delete()
