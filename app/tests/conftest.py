import os

import pytest

from app.views import app


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
