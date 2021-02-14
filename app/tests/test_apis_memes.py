import json

import pytest

from .. import settings


def describe_list():
    def describe_GET():
        @pytest.mark.slow
        def it_returns_example_image_urls(expect, client):
            request, response = client.get("/images", timeout=10)
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
            data = {"template_id": "iw", "text_lines[]": ["foo", "bar"]}
            request, response = client.post(
                "/images", data=json.dumps(data) if as_json else data
            )
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.png"
            }

        def it_redirects_if_requested(expect, client):
            data = {"template_id": "iw", "text_lines": ["abc"], "redirect": True}
            request, response = client.post("/images", data=data, allow_redirects=False)
            redirect = "http://localhost:5000/images/iw/abc.png"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        def it_requires_template_id(expect, client):
            data = {"text_lines": ["foo", "bar"]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 400
            expect(response.json) == {"error": '"template_id" is required'}

        def it_handles_unknown_template_id(expect, client, unknown_template):
            data = {"template_id": unknown_template.id, "text_lines": ["one", "two"]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 404
            expect(response.json) == {
                "url": "http://localhost:5000/images/unknown/one/two.png"
            }

        def it_handles_unknown_template_id_redirect(expect, client, unknown_template):
            data = {
                "template_id": unknown_template.id,
                "text_lines": ["one", "two"],
                "redirect": True,
            }
            request, response = client.post("/images", data=data, allow_redirects=False)
            redirect = "http://localhost:5000/images/unknown/one/two.png"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        def it_handles_missing_text_lines(expect, client):
            data = {"template_id": "iw"}
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {"url": "http://localhost:5000/images/iw.png"}

        def it_drops_trailing_blank_lines(expect, client):
            data = {"template_id": "iw", "text_lines": ["", "", "", ""]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {"url": "http://localhost:5000/images/iw.png"}

        def it_supports_slashes_to_indicate_blank_lines(expect, client):
            data = {"template_id": "iw", "text_lines": ["/", "2", "/", ""]}
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {"url": "http://localhost:5000/images/iw/_/2.png"}


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
        request, response = client.get(f"/images/{unknown_template.id}/test.png")
        expect(response.status) == 404
        expect(response.headers["content-type"]) == "image/png"

    def it_rejects_extremely_long_urls(expect, client):
        text = "test-" * 50
        request, response = client.get(f"/images/fry/{text}.jpg")
        expect(response.status) == 414
        expect(response.headers["content-type"]) == "image/jpeg"

    def describe_watermark():
        @pytest.fixture(autouse=True)
        def watermark_settings(monkeypatch, client):
            monkeypatch.setattr(settings, "DISABLED_WATERMARK", "blank")
            monkeypatch.setattr(settings, "DEFAULT_WATERMARK", "memegen.link")
            monkeypatch.setattr(settings, "ALLOWED_WATERMARKS", ["example.com"])
            monkeypatch.setattr(settings, "API_KEYS", ["sample"])

        @pytest.fixture
        def default_content(watermark_settings, client):
            request, response = client.get("/images/fry/test.png")
            return response.content

        def it_returns_a_unique_image(expect, client, default_content):
            request, response = client.get(
                "/images/fry/test.png?watermark=example.com",
                allow_redirects=False,
            )
            expect(response.status) == 200
            expect(len(response.content)) != len(default_content)

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_rejects_unknown_watermarks(expect, client, ext):
            request, response = client.get(
                f"/images/fry/test.{ext}?watermark=foobar",
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == f"/images/fry/test.{ext}"

        @pytest.mark.parametrize("ext", ["png", "jpg"])
        def it_removes_redundant_watermarks(expect, client, ext):
            request, response = client.get(
                f"/images/fry/test.{ext}?watermark=memegen.link",
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == f"/images/fry/test.{ext}"

        def it_can_be_disabled_by_referer(expect, client, default_content):
            request, response = client.get(
                "/images/fry/test.png?watermark=blank",
                headers={"REFERER": "http://example.com"},
                allow_redirects=False,
            )
            expect(response.status) == 200
            expect(len(response.content)) != len(default_content)

        def it_rejects_missing_referer(expect, client):
            request, response = client.get(
                "/images/fry/test.png?watermark=blank",
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == "/images/fry/test.png"

        def it_rejects_unknown_referer(expect, client):
            request, response = client.get(
                "/images/fry/test.png?watermark=blank",
                headers={"REFERER": "http://google.com"},
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == "/images/fry/test.png"

        def it_is_disabled_automatically_when_authenticated(expect, client):
            request, response = client.get(
                "/images/fry/test.png?watermark=ignored",
                headers={"X-API-KEY": "sample"},
                allow_redirects=False,
            )
            expect(response.status) == 200

        def it_rejects_invalid_authentication(expect, client):
            request, response = client.get(
                "/images/fry/test.png?watermark=blank",
                headers={"X-API-KEY": "foobar"},
                allow_redirects=False,
            )
            expect(response.status) == 301
            expect(response.headers["Location"]) == "/images/fry/test.png"

        def it_is_disabled_automatically_for_small_images(expect, client):
            small_content = client.get("/images/fry/test.png?width=300")[1].content
            request, response = client.get(
                "/images/fry/test.png?width=300&watermark=example.com",
                headers={"REFERER": "http://example.com"},
                allow_redirects=False,
            )
            expect(response.status) == 200
            expect(len(response.content)) == len(small_content)

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


def describe_automatic():
    def describe_POST():
        def it_requires_text(expect, client):
            request, response = client.post("/images/automatic")
            expect(response.status) == 400
            expect(response.json) == {"error": '"text" is required'}


def describe_custom():
    def describe_POST():
        @pytest.mark.parametrize("as_json", [True, False])
        def it_supports_custom_backgrounds(expect, client, as_json):
            data = {
                "image_url": "https://www.gstatic.com/webp/gallery/3.png",
                "text_lines[]": ["foo", "bar"],
                "extension": "jpg",
            }
            request, response = client.post(
                "/images/custom", data=json.dumps(data) if as_json else data
            )
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.jpg"
                "?background=https://www.gstatic.com/webp/gallery/3.png"
            }

        def it_redirects_if_requested(expect, client):
            data = {
                "image_url": "https://www.gstatic.com/webp/gallery/4.png",
                "text_lines": ["abc"],
                "redirect": True,
            }
            request, response = client.post(
                "/images/custom", data=data, allow_redirects=False
            )
            redirect = "http://localhost:5000/images/custom/abc.png?background=https://www.gstatic.com/webp/gallery/4.png"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect
