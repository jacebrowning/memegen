import json

import pytest


def describe_template_list():
    def describe_GET():
        @pytest.mark.slow
        def it_returns_all_templates(expect, client):
            request, response = client.get("/templates")
            expect(response.status) == 200


def describe_template_detail():
    def describe_GET():
        def it_includes_metadata(expect, client):
            request, response = client.get("/templates/iw")
            expect(response.status) == 200
            expect(response.json) == {
                "name": "Insanity Wolf",
                "key": "iw",
                "lines": 2,
                "styles": [],
                "blank": "http://localhost:5000/images/iw.png",
                "example": "http://localhost:5000/images/iw/DOES_TESTING/IN_PRODUCTION.png",
                "source": "http://knowyourmeme.com/memes/insanity-wolf",
                "_self": "http://localhost:5000/templates/iw",
            }

        def it_shortens_example_when_no_text(expect, client):
            request, response = client.get("/templates/mmm")
            expect(response.status) == 200
            expect(response.json["example"]) == "http://localhost:5000/images/mmm.png"

        def it_returns_404_when_missing(expect, client):
            request, response = client.get("/templates/foobar")
            expect(response.status) == 404

    def describe_POST():
        def it_returns_an_image_url(expect, client):
            data = {"text_lines": ["foo", "bar"], "extension": "jpg"}
            request, response = client.post("/templates/iw", data=json.dumps(data))
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.jpg"
            }

        def it_supports_custom_backgrounds(expect, client):
            data = {
                "image_url": "https://www.gstatic.com/webp/gallery/3.png",
                "text_lines": ["foo", "bar"],
                "extension": "jpg",
            }
            request, response = client.post("/templates/custom", data=json.dumps(data))
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.jpg"
                "?background=https://www.gstatic.com/webp/gallery/3.png"
            }

        @pytest.mark.parametrize("key", ["fry", "custom"])
        def it_redirects_if_requested(expect, client, key):
            data = {"text_lines": ["abc"], "redirect": True}
            request, response = client.post(
                f"/templates/{key}", data=json.dumps(data), allow_redirects=False
            )
            expect(response.status) == 302


def describe_image_list():
    def describe_GET():
        @pytest.mark.slow
        def it_returns_example_image_urls(expect, client):
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

        def it_accepts_form_data(expect, client):
            data = {"template_key": "iw", "text_lines[]": ["foo", "bar"]}
            request, response = client.post("/images", data=data)
            print(response.json)
            print(response.text)
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

        def it_redirects_if_requested(expect, client):
            data = {"template_key": "iw", "text_lines": ["abc"], "redirect": True}
            request, response = client.post(
                "/images", data=json.dumps(data), allow_redirects=False
            )
            expect(response.status) == 302


def describe_preview():
    def it_returns_an_image(expect, client):
        path = "/images/preview.jpg"
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == "image/jpeg"


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
        [
            ("/images/fry.png", "image/png"),
            ("/images/fry.jpg", "image/jpeg"),
        ],
    )
    def it_returns_blank_templates_when_no_slug(expect, client, path, content_type):
        request, response = client.get(path)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == content_type

    def it_handles_unknown_templates(expect, client):
        request, response = client.get("/images/unknown/test.png")
        expect(response.status) == 404
        expect(response.headers["content-type"]) == "image/png"

    def it_rejects_extremely_long_urls(expect, client):
        text = "test-" * 50
        request, response = client.get(f"/images/fry/{text}.jpg")
        expect(response.status) == 414
        expect(response.headers["content-type"]) == "image/jpeg"

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
        @pytest.mark.slow
        def it_supports_custom_templates(expect, client):
            request, response = client.get(
                "/images/custom/test.png"
                "?background=https://www.gstatic.com/webp/gallery/3.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        def it_requires_an_image_with_custom_templates(expect, client):
            request, response = client.get("/images/custom/test.png")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_invalid_urls(expect, client):
            request, response = client.get(
                "/images/custom/test.png" "?background=foobar"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_missing_urls(expect, client):
            request, response = client.get(
                "/images/custom/test.png"
                "?background=http://example.com/does_not_exist.png"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

    def describe_redirects():
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
            redirect = f"/images/custom/One_Two.{ext}?alt=http://example.com"
            expect(response.status) == 301
            expect(response.headers["Location"]) == redirect

        def it_handles_encoded_newlines(expect, client):
            request, response = client.get(
                "/images/fry/1 2%0A3.jpg", allow_redirects=False
            )
            redirect = "/images/fry/1_2~n3.jpg"
            expect(response.status) == 301
            expect(response.headers["Location"]) == redirect

    def describe_shortcuts():
        def it_redirects_to_example_image_when_no_extension(expect, client):
            request, response = client.get("/images/fry", allow_redirects=False)
            redirect = "/images/fry/NOT_SURE_IF_TROLLING/OR_JUST_STUPID"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        def it_redirects_to_custom_image_when_no_extension(expect, client):
            request, response = client.get("/images/fry/test", allow_redirects=False)
            expect(response.status) == 302
            expect(response.headers["Location"]) == "/images/fry/test.png"

    def describe_legacy():
        @pytest.mark.slow
        def it_accepts_alt_for_template(expect, client):
            request, response = client.get(
                "/images/custom/test.png"
                "?alt=https://www.gstatic.com/webp/gallery/3.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        @pytest.mark.slow
        def it_accepts_alt_for_style(expect, client):
            request, response = client.get("/images/sad-biden/test.png?style=scowl")
            expect(response.status) == 200

            request, response2 = client.get("/images/sad-biden/test.png?alt=scowl")
            expect(response.status) == 200

            expect(len(response.content)) == len(response2.content)

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_redirects_to_example_image(expect, client, ext):
            request, response = client.get(f"/fry.{ext}", allow_redirects=False)
            redirect = f"/images/fry/NOT_SURE_IF_TROLLING/OR_JUST_STUPID.{ext}"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_redirects_to_custom_image(expect, client, ext):
            request, response = client.get(f"/fry/test.{ext}", allow_redirects=False)
            expect(response.status) == 302
            expect(response.headers["Location"]) == f"/images/fry/test.{ext}"
