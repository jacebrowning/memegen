import pytest


def describe_auth():
    def describe_POST():
        def it_returns_401_when_unauthenticated(expect, client):
            request, response = client.post("/auth")
            expect(response.status) == 401
            expect(response.json) == {"error": "API key missing or invalid."}


def describe_image_preview():
    @pytest.fixture
    def path():
        return "/images/preview.jpg"

    def it_returns_an_image(expect, client, path):
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == "image/jpeg"

    def it_supports_custom_templates(expect, client, path):
        request, response = client.get(
            path + "?template=https://www.gstatic.com/webp/gallery/1.png"
        )
        expect(response.status) == 200
        expect(response.headers["content-type"]) == "image/jpeg"

    def it_handles_invalid_urls(expect, client, path):
        request, response = client.get(path + "?template=http://example.com/foobar.jpg")
        expect(response.status) == 200
        expect(response.headers["content-type"]) == "image/jpeg"

    def it_handles_invalid_keys(expect, client, path, unknown_template):
        request, response = client.get(path + f"?template={unknown_template.id}")
        expect(response.status) == 200
        expect(response.headers["content-type"]) == "image/jpeg"
