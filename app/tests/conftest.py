import pytest

from app.views import app


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False


@pytest.fixture
def client():
    return app.test_client
