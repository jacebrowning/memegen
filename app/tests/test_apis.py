import json

import pytest


def describe_template_list():
    def describe_GET():
        def it_returns_all_templates(expect, client):
            request, response = client.get("/templates")
            expect(response.status) == 200


def describe_template_detail():
    def describe_GET():
        def it_returns_sample_images(expect, client):
            request, response = client.get("/templates/iw")
            expect(response.status) == 200
            expect(response.json) == {
                "name": "Insanity Wolf",
                "key": "iw",
                "styles": [],
                "blank": "http://localhost:5000/images/iw.png",
                "sample": "http://localhost:5000/images/iw/DOES_TESTING/IN_PRODUCTION.png",
                "source": "http://knowyourmeme.com/memes/insanity-wolf",
                "_self": "http://localhost:5000/templates/iw",
            }

        def it_returns_404_when_missing(expect, client):
            request, response = client.get("/templates/foobar")
            expect(response.status) == 404


def describe_image_list():
    def describe_GET():
        def it_returns_sample_image_urls(expect, client):
            request, response = client.get("/images")
            expect(response.status) == 200
            expect(response.json).contains(
                {
                    "url": "http://localhost:5000/images/iw/DOES_TESTING/IN_PRODUCTION.png",
                    "template": "http://localhost:5000/templates/iw",
                }
            )

    def describe_POST():
        def it_returns_an_image_url(expect, client):
            data = {"template_key": "iw", "text_lines": ["foo", "bar"]}
            request, response = client.post("/images", data=json.dumps(data))
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.png"
            }

        def it_requires_template_key(expect, client):
            data = {"text_lines": ["foo", "bar"]}
            request, response = client.post("/images", data=json.dumps(data))
            expect(response.status) == 400
            expect(response.json) == {"error": '"template_key" is required'}

        def it_handles_missing_text_lines(expect, client):
            data = {"template_key": "iw"}
            request, response = client.post("/images", data=json.dumps(data))
            expect(response.status) == 201
            expect(response.json) == {"url": "http://localhost:5000/images/iw/_.png"}


def describe_image_detail():
    @pytest.mark.parametrize(
        ("path", "content_type"),
        [
            ("/images/fry/test.png", "image/png"),
            ("/images/fry/test.jpg", "image/jpeg"),
        ],
    )
    def it_returns_an_image(expect, client, path, content_type):
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == content_type

    @pytest.mark.parametrize(
        ("path", "content_type"),
        [("/images/fry.png", "image/png"), ("/images/fry.jpg", "image/jpeg"),],
    )
    def it_returns_blank_templates_when_no_slug(expect, client, path, content_type):
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == content_type

    def it_handles_unknown_templates(expect, client):
        request, response = client.get("/images/unknown/test.png")
        expect(response.status) == 404
        expect(response.headers["content-type"]) == "image/png"

    def describe_styles():
        def it_supports_alternate_styles(expect, client):
            request, response = client.get("/images/ds/one/two.png?style=maga")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        def it_rejects_invalid_styles(expect, client):
            request, response = client.get("/images/ds/one/two.png?style=foobar")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

    def describe_custom():
        # TODO: Figure out why this test takes 5+ seconds (pytest --durations=0)
        def it_supports_custom_templates(expect, client):
            request, response = client.get(
                "/images/custom/test.png"
                "?alt=https://www.gstatic.com/webp/gallery/3.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        def it_requires_an_image_with_custom_templates(expect, client):
            request, response = client.get("/images/custom/test.png")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_invalid_urls_with_custom_templates(expect, client):
            request, response = client.get(
                "/images/custom/test.png" "?alt=http://example.com/does_not_exist.png"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

    def describe_redirect():
        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_redirects_to_normalized_slug(expect, client, ext):
            request, response = client.get(
                f"/images/fry/One Two.{ext}", allow_redirects=False
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == f"/images/fry/One_Two.{ext}"

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_preserves_query_params_when_redirecting(expect, client, ext):
            request, response = client.get(
                f"/images/custom/One Two.{ext}?alt=http://example.com",
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(
                response.headers["Location"]
            ) == f"/images/custom/One_Two.{ext}?alt=http://example.com"

        def it_redirects_to_sample_image_when_no_extension(expect, client):
            request, response = client.get("/images/fry", allow_redirects=False)
            expect(response.status) == 302
            expect(
                response.headers["Location"]
            ) == "/images/fry/NOT_SURE_IF_TROLLING/OR_JUST_STUPID"
