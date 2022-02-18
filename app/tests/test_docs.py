import pytest
from pkg_resources import get_distribution


def describe_spec():
    def it_contains_the_version(expect, client):
        version = get_distribution("memegen").version
        request, response = client.get("/docs/openapi.json")
        expect(response.status) == 200
        if "b" not in version:
            expect(response.json["info"]["version"]) == version


@pytest.mark.xfail(reason="Requires JavaScript")
def describe_ui():
    def it_contains_image_routes(expect, client):
        request, response = client.get("/docs")
        expect(response.status) == 200
        expect(response.text).contains("Display a custom meme")

    def it_contains_redirect_routes(expect, client):
        request, response = client.get("/docs")
        expect(response.status) == 200
        expect(response.text).contains("Redirect to a custom image")
