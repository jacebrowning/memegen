import json

import pytest


def describe_root():
    def it_returns_all_routes(expect, client):
        request, response = client.get("/api")
        expect(response.status) == 200
        expect(response.json) == {
            "templates": "http://localhost:5000/api/templates",
            "images": "http://localhost:5000/api/images",
            "docs": "http://localhost:5000/api/docs",
        }


def describe_template_list():
    def describe_GET():
        def it_returns_all_templates(expect, client):
            request, response = client.get("/api/templates")
            expect(response.status) == 200


def describe_template_detail():
    def describe_GET():
        def it_returns_sample_images(expect, client):
            request, response = client.get("/api/templates/iw")
            expect(response.status) == 200
            expect(response.json) == {
                "name": "Insanity Wolf",
                "styles": [],
                "blank": "http://localhost:5000/api/images/iw.png",
                "sample": "http://localhost:5000/api/images/iw/does_testing/in_production.png",
                "source": "http://knowyourmeme.com/memes/insanity-wolf",
                "_self": "http://localhost:5000/api/templates/iw",
            }

        def it_returns_404_when_missing(expect, client):
            request, response = client.get("/api/templates/foobar")
            expect(response.status) == 404


def describe_image_list():
    def describe_GET():
        def it_returns_sample_image_urls(expect, client):
            request, response = client.get("/api/images")
            expect(response.status) == 200
            expect(response.json).contains(
                {
                    "url": "http://localhost:5000/api/images/iw/does_testing/in_production.png"
                }
            )

    def describe_POST():
        def it_returns_an_image_url(expect, client):
            data = {"key": "iw", "lines": ["foo", "bar"]}
            request, response = client.post("/api/images", data=json.dumps(data))
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/api/images/iw/foo/bar.png"
            }


def describe_image_detail():
    @pytest.mark.parametrize(
        ("path", "content_type"),
        [
            ("/api/images/fry/test.png", "image/png"),
            ("/api/images/fry/test.jpg", "image/jpeg"),
        ],
    )
    def it_returns_an_image(expect, client, path, content_type):
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == content_type

    @pytest.mark.parametrize(
        ("path", "content_type"),
        [("/api/images/fry.png", "image/png"), ("/api/images/fry.jpg", "image/jpeg"),],
    )
    def it_returns_blank_templates_when_no_slug(expect, client, path, content_type):
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == content_type

    def it_handles_unknown_templates(expect, client):
        request, response = client.get("/api/images/unknown/test.png")
        expect(response.status) == 404
        expect(response.headers["content-type"]) == "image/png"

    def describe_styles():
        def it_supports_alternate_styles(expect, client):
            request, response = client.get("/api/images/ds/one/two.png?style=maga")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        def it_rejects_invalid_styles(expect, client):
            request, response = client.get("/api/images/ds/one/two.png?style=foobar")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

    def describe_custom():
        # TODO: Figure out why this test takes 5+ seconds (pytest --durations=0)
        def it_supports_custom_templates(expect, client):
            request, response = client.get(
                "/api/images/custom/test.png"
                "?alt=https://www.gstatic.com/webp/gallery/3.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        def it_requires_an_image_with_custom_templates(expect, client):
            request, response = client.get("/api/images/custom/test.png")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_invalid_urls_with_custom_templates(expect, client):
            request, response = client.get(
                "/api/images/custom/test.png"
                "?alt=http://example.com/does_not_exist.png"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

    def describe_redirect():
        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_redirects_to_normalized_slug(expect, client, ext):
            request, response = client.get(
                f"/api/images/fry/One Two.{ext}", allow_redirects=False
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == f"/api/images/fry/One_Two.{ext}"

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_preserves_query_params_when_redirecting(expect, client, ext):
            request, response = client.get(
                f"/api/images/custom/One Two.{ext}?alt=http://example.com",
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(
                response.headers["Location"]
            ) == f"/api/images/custom/One_Two.{ext}?alt=http://example.com"
