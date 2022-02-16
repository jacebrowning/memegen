import os

import pytest
import requests


@pytest.fixture(scope="session")
def url():
    return os.getenv("SITE", "http://localhost:5000")


def test_get_templates(expect, url):
    response = requests.get(f"{url}/templates")
    expect(response.status_code) == 200


def test_post_images(expect, url):
    params = {"template_id": "iw", "text_lines": ["test", "deployment"]}
    response = requests.post(f"{url}/images", json=params)
    expect(response.status_code) == 201
    expect(response.json()["url"]).endswith("/images/iw/test/deployment.png")


def test_get_examples(expect, url):
    response = requests.get(f"{url}/examples")
    expect(response.status_code) == 200


def test_get_image(expect, url):
    response = requests.get(f"{url}/images/iw/tests_code/in_production.jpg")
    expect(response.status_code) == 200
    expect(response.headers["Content-Type"]) == "image/jpeg"


def test_get_image_custom(expect, url):
    response = requests.get(
        f"{url}/images/custom/test.png"
        "?alt=https://www.gstatic.com/webp/gallery/1.jpg"
    )
    expect(response.status_code) == 200
    expect(response.headers["Content-Type"]) == "image/png"


def test_swagger(expect, url):
    response = requests.get(
        f"https://validator.swagger.io/validator/debug?url="
        f"{url}%2Fdocs%2Fopenapi.json"
    )
    expect(response.status_code) == 200
    expect(response.json()) == {}
