import pytest

from app.views import app


@pytest.fixture
def client():
    return app.test_client
