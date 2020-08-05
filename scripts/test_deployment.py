import os

import pytest
import requests


@pytest.fixture
def url():
    return os.getenv("SITE", "http://localhost:5000")


def test_post_images(expect, url):
    params = {"key": "iw", "lines": ["test", "deployment"]}
    response = requests.post(f"{url}/api/images", json=params)
    expect(response.status_code) == 201
    expect(response.json()["url"]).endswith("/api/images/iw/test/deployment.png")
