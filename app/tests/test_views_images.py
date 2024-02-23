import json
from unittest.mock import AsyncMock, patch

import pytest

from .. import settings


def describe_list():
    def describe_GET():
        @pytest.mark.slow
        def it_returns_example_image_urls(expect, client):
            request, response = client.get("/images", timeout=15)
            expect(response.status) == 200
            expect(response.json).contains(
                {
                    "url": "http://localhost:5000/images/iw/does_testing/in_production.png",
                    "template": "http://localhost:5000/templates/iw",
                }
            )

        @pytest.mark.slow
        def it_can_filter_examples(expect, client):
            request, response = client.get("/images?filter=awesome", timeout=15)
            expect(response.status) == 200
            expect(len(response.json)) == 3

    def describe_POST():
        @pytest.mark.parametrize("as_json", [True, False])
        def it_returns_an_image_url(expect, client, as_json):
            data = {"template_id": "iw", "text_lines[]": ["foo", "bar"]}
            kwargs: dict = {"content": json.dumps(data)} if as_json else {"data": data}
            request, response = client.post("/images", **kwargs)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.png"
            }

        def it_lowercases_text_for_default_templates(expect, client):
            data = {
                "template_id": "iw",
                "text_lines[]": ["foo", "Bar"],
            }
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.png"
            }

        def it_preserves_text_case_for_top_layouts(expect, client):
            data = {
                "template_id": "iw",
                "text_lines[]": ["foo", "Bar"],
                "layout": "top",
            }
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/Bar.png?layout=top"
            }

        def it_removes_redundant_styles(expect, client):
            data = {
                "template_id": "iw",
                "text_lines[]": ["foo", "bar"],
                "style[]": [" ", "test", "default"],
                "font": "impact",
            }
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.png?style=default,test&font=impact"
            }

        def it_returns_gif_when_animated(expect, client):
            data = {
                "template_id": "iw",
                "text_lines[]": ["foo", "bar"],
                "style": "animated",
            }
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.gif"
            }

        def it_prefers_extension_over_animated_style(expect, client):
            data = {
                "template_id": "iw",
                "text_lines[]": ["foo", "bar"],
                "style": "animated",
                "extension": "webp",
            }
            request, response = client.post("/images", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.webp"
            }

        def it_redirects_if_requested(expect, client):
            data = {"template_id": "iw", "text_lines": ["abc"], "redirect": True}
            request, response = client.post("/images", data=data, allow_redirects=False)
            redirect = "http://localhost:5000/images/iw/abc.png?status=201"
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
            redirect = "http://localhost:5000/images/unknown/one/two.png?status=201"
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

        def it_handles_invalid_json(expect, client):
            request, response = client.post("/images", content="???")
            expect(response.status) == 400
            expect(response.json) == {"error": '"template_id" is required'}


def describe_detail():
    @pytest.mark.slow
    @pytest.mark.parametrize(
        ("path", "content_type"),
        [
            ("/images/fry.gif", "image/gif"),
            ("/images/fry.jpg", "image/jpeg"),
            ("/images/fry.png", "image/png"),
            ("/images/fry.webp", "image/webp"),
            ("/images/fry/test.gif", "image/gif"),
            ("/images/fry/test.jpg", "image/jpeg"),
            ("/images/fry/test.png", "image/png"),
            ("/images/fry/test.webp", "image/webp"),
        ],
    )
    def it_returns_an_image(expect, client, path, content_type):
        request, response = client.get(path, timeout=15)
        expect(response.status) == 200
        expect(response.headers["content-type"]) == content_type

    def it_handles_placeholder_templates(expect, client):
        request, response = client.get("/images/string/test.png")
        expect(response.status) == 200
        expect(response.headers["content-type"]) == "image/png"

    def it_handles_unknown_templates(expect, client, unknown_template):
        request, response = client.get(f"/images/{unknown_template.id}/test.png")
        expect(response.status) == 404
        expect(response.headers["content-type"]) == "image/png"

    def it_rejects_invalid_extensions(expect, client):
        request, response = client.get("/images/fry/test.foobar")
        expect(response.status) == 422
        expect(response.headers["content-type"]) == "image/png"

    def it_rejects_extremely_small_sizes(expect, client):
        request, response = client.get("/images/fry/test.jpg?width=9")
        expect(response.status) == 422
        expect(response.headers["content-type"]) == "image/jpeg"

    def it_rejects_invalid_sizes(expect, client):
        request, response = client.get("/images/fry/test.jpg?width=abc")
        expect(response.status) == 422
        expect(response.headers["content-type"]) == "image/jpeg"

    def it_rejects_extremely_long_urls(expect, client):
        text = "test-" * 50
        request, response = client.get(f"/images/fry/{text}.jpg")
        expect(response.status) == 414
        expect(response.headers["content-type"]) == "image/jpeg"

    def describe_font():
        def it_rejects_unknown_fonts(expect, client):
            request, response = client.get("/images/fry/test.png?font=foobar")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        def it_ignores_placeholder_values(expect, client):
            request, response = client.get("/images/fry/test.png?font=string")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

    def describe_watermark():
        @pytest.fixture(autouse=True)
        def watermark_settings(monkeypatch, client):
            monkeypatch.setattr(settings, "ALLOWED_WATERMARKS", ["example.com"])

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

        @pytest.mark.parametrize("extension", ["png", "jpg"])
        def it_rejects_unknown_watermarks(expect, client, extension):
            request, response = client.get(
                f"/images/fry/test.{extension}?watermark=foobar",
                allow_redirects=False,
            )
            expect(response.status) == 302
            expect(response.headers["Location"]) == f"/images/fry/test.{extension}"

        @pytest.mark.parametrize("extension", ["png", "jpg"])
        def it_removes_redundant_watermarks(expect, client, extension):
            request, response = client.get(
                f"/images/fry/test.{extension}?watermark=memegen.link",
                allow_redirects=False,
            )
            expect(response.status) == 302
            expect(response.headers["Location"]) == f"/images/fry/test.{extension}"

        @patch(
            "app.utils.meta.authenticate",
            AsyncMock(return_value={"image_access": True}),
        )
        def it_accepts_custom_values_when_authenticated(expect, client):
            request, response = client.get(
                "/images/fry/test.png?watermark=mydomain.com",
                allow_redirects=False,
            )
            expect(response.status) == 200

        def it_rejects_invalid_authentication(expect, client):
            request, response = client.get(
                "/images/fry/test.png?watermark=blank",
                headers={"X-API-KEY": "foobar"},
                allow_redirects=False,
            )
            expect(response.status) == 302
            expect(response.headers["Location"]) == "/images/fry/test.png"

        def it_is_disabled_automatically_for_small_images(expect, client):
            small_content = client.get("/images/fry/test.png?width=300")[1].content
            request, response = client.get(
                "/images/fry/test.png?width=300&watermark=example.com",
                allow_redirects=False,
            )
            expect(response.status) == 200
            expect(len(response.content)) == len(small_content)

    def describe_styles():
        @pytest.fixture(
            params=[
                "/images/ds/one/two.png?",
                "/images/custom/test.png?background=https://www.gstatic.com/webp/gallery/3.jpg&",
            ]
        )
        def base_url(request):
            return request.param

        @pytest.mark.slow
        def it_supports_alternate_styles(expect, client):
            request, response = client.get("/images/ds/one/two.png?style=maga")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        @pytest.mark.parametrize("slug", ["ds", "ds/one/two"])
        def it_redirects_to_gif_when_animated(expect, client, slug):
            request, response = client.get(
                f"/images/{slug}.png?style=animated", allow_redirects=False
            )
            redirect = f"/images/{slug}.gif"
            expect(response.status) == 301
            expect(response.headers["Location"]) == redirect

        @pytest.mark.slow
        def it_rejects_invalid_styles(expect, client, base_url):
            request, response = client.get(base_url + "style=foobar")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        @pytest.mark.slow
        def it_ignores_placeholder_values(expect, client, base_url):
            request, response = client.get(base_url + "style=string")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

    def describe_overlay():
        @pytest.fixture(
            params=[
                "/images/fine/test.png?",
                "/images/custom/test.png?background=https://www.gstatic.com/webp/gallery/3.jpg&",
            ]
        )
        def base_url(request):
            return request.param

        def it_supports_custom_styles(expect, client, base_url):
            request, response = client.get(
                base_url + "style=https://www.gstatic.com/webp/gallery/4.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        @pytest.mark.slow
        def it_requires_image_urls(expect, client, base_url):
            request, response = client.get(base_url + "style=http://example.com")
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

        @pytest.mark.slow
        def it_handles_missing_urls(expect, client, base_url):
            request, response = client.get(
                base_url + "style=http://example.com/does_not_exist.png"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

    def describe_custom():
        def it_supports_custom_templates(expect, client):
            request, response = client.get(
                "/images/custom/test.png"
                "?background=https://www.gstatic.com/webp/gallery/3.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        @pytest.mark.slow
        def it_supports_custom_templates_with_animation(expect, client):
            request, response = client.get(
                "/images/custom/test/test.gif"
                "?background=https://www.gstatic.com/webp/gallery/4.jpg"
                "&start=0.1&stop=0.5,0.9",
                timeout=15,
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/gif"

        def it_requires_an_image_with_custom_templates(expect, client):
            request, response = client.get("/images/custom/test.png")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_invalid_urls(expect, client):
            request, response = client.get("/images/custom/test.png?background=foobar")
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_missing_urls(expect, client):
            request, response = client.get(
                "/images/custom/test.png"
                "?background=http://example.com/does_not_exist.png"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

        def it_handles_redirect_urls(expect, client):
            request, response = client.get(
                "/images/custom/test.png?background=https://i.imgur.com/zw1eny2.jpg"
            )
            expect(response.status) == 415
            expect(response.headers["content-type"]) == "image/png"

        def it_ignores_placeholder_values(expect, client):
            request, response = client.get(
                "/images/custom/string.png?background=string"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"


def describe_automatic():
    def describe_POST():
        def it_requires_text(expect, client):
            request, response = client.post("/images/automatic")
            expect(response.status) == 400
            expect(response.json) == {"error": '"text" is required'}

        @patch(
            "app.utils.meta.search",
            AsyncMock(
                return_value=[
                    {
                        "image_url": "http://example.com/images/example.png"
                        + "?background=https://www.gstatic.com/webp/gallery/3.png",
                        "generator": "Test",
                        "confidence": 0.5,
                    }
                ]
            ),
        )
        @pytest.mark.parametrize("as_json", [True, False])
        def it_normalizes_the_url(expect, client, as_json):
            data = {"text": "example"}
            kwargs: dict = {"content": json.dumps(data)} if as_json else {"data": data}
            request, response = client.post("/images/automatic", **kwargs)
            expect(response.json) == {
                "url": "http://localhost:5000/images/example.png"
                + "?background=https://www.gstatic.com/webp/gallery/3.png",
                "generator": "Test",
                "confidence": 0.5,
            }

        def it_handles_invalid_json(expect, client):
            request, response = client.post("/images/automatic", content="???")
            expect(response.status) == 400
            expect(response.json) == {"error": '"text" is required'}


def describe_custom():
    def describe_POST():
        @pytest.mark.parametrize("as_json", [True, False])
        def it_supports_custom_backgrounds(expect, client, as_json):
            data = {
                "background": "http://example.com",
                "text_lines[]": ["foo", "bar"],
            }
            kwargs: dict = {"content": json.dumps(data)} if as_json else {"data": data}
            request, response = client.post("/images/custom", **kwargs)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.png"
                "?background=http://example.com"
            }

        def it_escapes_query_parameters(expect, client):
            data = {
                "background": "https://cdn.discordapp.com/attachments/1/2/stare.png?ex=a1&is=b2&hm=c3",
                "text_lines[]": ["foo", "bar"],
            }
            request, response = client.post("/images/custom", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.png"
                "?background=https://cdn.discordapp.com/attachments/1/2/stare.png%3Fex=a1%26is=b2%26hm=c3"
            }

        def it_returns_gif_when_background_is_gif(expect, client):
            data = {
                "background": "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif",
                "text_lines[]": ["foo", "bar"],
            }
            request, response = client.post("/images/custom", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.gif"
                "?background=https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
            }

        def it_redirects_if_requested(expect, client):
            data = {
                "background": "https://www.gstatic.com/webp/gallery/4.png",
                "text_lines": ["abc"],
                "redirect": True,
            }
            request, response = client.post(
                "/images/custom", data=data, allow_redirects=False
            )
            redirect = "http://localhost:5000/images/custom/abc.png?background=https://www.gstatic.com/webp/gallery/4.png&status=201"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

    def describe_GET():
        @patch(
            "app.utils.meta.search",
            AsyncMock(
                return_value=[{"image_url": "http://example.com/images/example.png"}]
            ),
        )
        def it_normalizes_the_url(expect, client):
            request, response = client.get("/images/custom")
            expect(response.json) == [
                {"url": "http://localhost:5000/images/example.png"}
            ]

        @patch(
            "app.utils.meta.search",
            AsyncMock(
                return_value=[
                    {
                        "image_url": "http://example.com/images/example.png"
                        + "?background=https://www.gstatic.com/webp/gallery/3.png"
                    }
                ]
            ),
        )
        def it_normalizes_the_url_with_background(expect, client):
            request, response = client.get("/images/custom")
            expect(response.json) == [
                {
                    "url": "http://localhost:5000/images/example.png"
                    + "?background=https://www.gstatic.com/webp/gallery/3.png"
                }
            ]
