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

    def it_describes_image_parameters_consistently():
        request, response = client.get(URL)
        expect(response.status) == 200
        paths = response.json["paths"]

        def get_descriptions(path):
            parameters = paths[path]["get"]["parameters"]
            return {
                p["name"]: p["description"] for p in parameters if p["in"] == "query"
            }

        blank = get_descriptions("/images/{template_filename}")
        text = get_descriptions("/images/{template_id}/{text_filepath}")
        expect(blank) == text
        expect(text["layout"]).contains("`default` or `top`")
        expect(get_descriptions("/images/preview.jpg")["layout"]).contains(
            "`default` or `top`"
        )


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
