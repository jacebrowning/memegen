import os

import pytest

from .. import settings
from ..main import app
from ..models import Template


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False
    settings.ALLOWED_EXTENSIONS.append("apng")


def pytest_runtest_setup(item):
    for marker in item.iter_markers(name="slow"):
        if "SKIP_SLOW" in os.environ:
            pytest.skip("slow test")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "REMOTE_TRACKING_URL", None)
    return app.test_client


@pytest.fixture
def unknown_template():
    template = Template.objects.get_or_create("unknown")
    template.delete()
    yield template
    template.delete()
