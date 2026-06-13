from importlib.metadata import version as get_version

import pytest


def describe_spec(expect, client):

    URL = "/docs/openapi.json"

    def it_contains_the_version():
        version = get_version("memegen")
        request, response = client.get(URL)
        expect(response.status) == 200
        if "b" not in version:
            expect(response.json["info"]["version"]) == version

    def it_links_to_the_api_guide():
        request, response = client.get(URL)
        expect(response.status) == 200
        expect(response.json["externalDocs"]["url"]) == "https://memegen.link/guide/"


@pytest.mark.xfail(reason="Requires JavaScript")
def describe_ui(expect, client):
    def it_contains_image_routes():
        request, response = client.get("/docs")
        expect(response.status) == 200
        expect(response.text).contains("Display a custom meme")

    def it_contains_redirect_routes():
        request, response = client.get("/docs")
        expect(response.status) == 200
        expect(response.text).contains("Redirect to a custom image")
