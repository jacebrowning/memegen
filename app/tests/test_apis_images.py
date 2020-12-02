import json

import pytest

from .. import settings


def describe_list():
    def describe_GET():
        @pytest.mark.slow
        def it_returns_example_image_urls(expect, client):
            request, response = client.get("/images")
            expect(response.status) == 200
            expect(response.json).contains(
                {
                    "url": "http://localhost:5000/images/iw/does_testing/in_production.jpg",
                    "template": "http://localhost:5000/templates/iw",
                }
            )

    def describe_POST():
        @pytest.mark.parametrize("as_json", [True, False])
        def it_returns_an_image_url(expect, client, as_json):
            data = {"template_key": "iw", "text_lines[]": ["foo", "bar"]}
            request, response = client.post(
                "/images", data=json.dumps(data) if as_json else data
            )
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.png"
            }

        def it_redirects_if_requested(expect, client):
            data = {"template_key": "iw", "text_lines": ["abc"], "redirect": True}
            request, response = client.post("/images", data=data, allow_redirects=False)
            redirect = "http://localhost:5000/images/iw/abc.png"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        def it_requires_template_key(expect, client):
            data = {"text_lines": ["foo", "bar"]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 400
            expect(response.json) == {"error": '"template_key" is required'}

        def it_handles_unknown_template_key(expect, client, unknown_template):
            data = {"template_key": unknown_template.key, "text_lines": ["one", "two"]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 404
            expect(response.json) == {
                "url": "http://localhost:5000/images/unknown/one/two.png"
            }

        def it_handles_unknown_template_key_redirect(expect, client, unknown_template):
            data = {
                "template_key": unknown_template.key,
                "text_lines": ["one", "two"],
                "redirect": True,
            }
            request, response = client.post("/images", data=data, allow_redirects=False)
            redirect = "http://localhost:5000/images/unknown/one/two.png"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        def it_handles_missing_text_lines(expect, client):
            data = {"template_key": "iw"}
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {"url": "http://localhost:5000/images/iw.png"}

        def it_drops_trailing_blank_lines(expect, client):
            data = {"template_key": "iw", "text_lines": ["", "", "", ""]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {"url": "http://localhost:5000/images/iw.png"}


def describe_detail():
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

    def it_handles_unknown_templates(expect, client, unknown_template):
        request, response = client.get(f"/images/{unknown_template.key}/test.png")
        expect(response.status) == 404
        expect(response.headers["content-type"]) == "image/png"

    def it_rejects_extremely_long_urls(expect, client):
        text = "test-" * 50
        request, response = client.get(f"/images/fry/{text}.jpg")
        expect(response.status) == 414
        expect(response.headers["content-type"]) == "image/jpeg"

    def describe_watermark():
        def it_returns_a_unique_image(expect, client, monkeypatch):
            monkeypatch.setattr(settings, "ALLOWED_WATERMARKS", ["test"])
            request, response = client.get("/images/fry/test.png")
            request, response2 = client.get("/images/fry/test.png?watermark=test")
            expect(len(response.content)) != len(response2.content)

        def it_can_be_disabled(expect, client, monkeypatch):
            monkeypatch.setattr(settings, "DEFAULT_WATERMARK", "")
            request, response = client.get("/images/fry/test.png")
            request, response2 = client.get("/images/fry/test.png?watermark=none")
            expect(len(response.content)) == len(response2.content)

        def it_is_disabled_automatically_for_small_images(expect, client, monkeypatch):
            monkeypatch.setattr(settings, "ALLOWED_WATERMARKS", ["test"])
            request, response = client.get("/images/fry/test.png?width=300")
            request, response2 = client.get(
                "/images/fry/test.png?width=300&watermark=test"
            )
            expect(len(response.content)) == len(response2.content)

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_rejects_unknown_values(expect, client, ext):
            request, response = client.get(
                f"/images/fry/test.{ext}?watermark=foobar", allow_redirects=False
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == f"/images/fry/test.{ext}"

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_removes_redundant_values(expect, client, monkeypatch, ext):
            monkeypatch.setattr(settings, "DEFAULT_WATERMARK", "memegen.link")
            request, response = client.get(
                f"/images/fry/test.{ext}?watermark=memegen.link", allow_redirects=False
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == f"/images/fry/test.{ext}"

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
