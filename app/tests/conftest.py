import os
import shutil
from pathlib import Path

import log
import pytest

from .. import settings, utils
from ..main import app
from ..models import Template


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False
    settings.ALLOWED_EXTENSIONS.append("apng")
    settings.DEBUG = False


def pytest_runtest_setup(item):
    for marker in item.iter_markers(name="slow"):
        if "SKIP_SLOW" in os.environ:
            pytest.skip("slow test")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "REMOTE_TRACKING_URL", None)
    return app.test_client


@pytest.fixture(scope="session")
def template():
    return Template.objects.get("icanhas")


@pytest.fixture
def unknown_template():
    t = Template.objects.get_or_create("unknown")
    t.delete()
    yield t
    t.delete()


@pytest.fixture(scope="session")
def images():
    path = settings.TEST_IMAGES_DIRECTORY
    path.mkdir(exist_ok=True)

    if "SKIP_SLOW" not in os.environ:
        return path

    flag = path / ".flag"
    if flag.exists():
        age = Path(utils.images.__file__).stat().st_mtime - flag.stat().st_mtime
        log.info(f"Test images are {age} seconds old")
        if age > 5 * 60:
            log.warn("Deleting stale test images")
            shutil.rmtree(path)
            path.mkdir()

    flag.touch()
    return path
