import pytest

from .. import settings


def describe_image_redirects(expect, client):
    @pytest.mark.parametrize("extension", ["png", "jpg"])
    def it_redirects_to_normalized_slug(extension):
        request, response = client.get(
            f"/images/fry/One Two.{extension}", allow_redirects=False
        )
        expect(response.status) == 301
        expect(response.headers["Location"]) == f"/images/fry/One_Two.{extension}"

    @pytest.mark.parametrize("extension", ["png", "jpg"])
    def it_preserves_query_params_when_redirecting(extension):
        request, response = client.get(
            f"/images/custom/One Two.{extension}?background=http://example.com",
            allow_redirects=False,
        )
        redirect = f"/images/custom/One_Two.{extension}?background=http://example.com"
        expect(response.status) == 301
        expect(response.headers["Location"]) == redirect

    def it_fixes_misplaced_query_params_on_path():
        request, response = client.get(
            "/images/fry/test&width=99&height=99", allow_redirects=False
        )
        redirect = "/images/fry/test.png?width=99&height=99"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    def it_fixes_misplaced_file_extension():
        request, response = client.get("/images/fry/.jpg", allow_redirects=False)
        redirect = "/images/fry.jpg"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    @pytest.mark.parametrize("extra", ["/", '"'])
    def it_fixes_extra_trailing_characters(extra):
        request, response = client.get(
            "/images/fry/test.jpg" + extra, allow_redirects=False
        )
        redirect = "/images/fry/test.jpg"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    def it_fixes_misplaced_query_params_on_image():
        request, response = client.get(
            "/images/fry/test.jpg&width=99&height=99", allow_redirects=False
        )
        redirect = "/images/fry/test.jpg?width=99&height=99"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    def it_truncates_invalid_path_values():
        request, response = client.get(
            "/images/fry/test//style=foobar", allow_redirects=False
        )
        redirect = "/images/fry/test.png"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    def it_handles_encoded_newlines():
        request, response = client.get("/images/fry/1 2%0A3.jpg", allow_redirects=False)
        redirect = "/images/fry/1_2~n3.jpg"
        expect(response.status) == 301
        expect(response.headers["Location"]) == redirect


def describe_path_redirects(expect, client):
    def it_redirects_to_example_image_when_no_extension():
        request, response = client.get("/images/fry", allow_redirects=False)
        redirect = "/images/fry/not_sure_if_trolling/or_just_stupid.gif"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    def it_redirects_to_custom_image_when_text_but_no_extension():
        request, response = client.get(
            "/images/fry/foo bar/._XD\\XD", allow_redirects=False
        )
        expect(response.status) == 302
        expect(response.headers["Location"]) == "/images/fry/foo_bar/._XD~bXD.png"

    def it_returns_gallery_view_when_debug(monkeypatch):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get("/images/fry/test")
        expect(response.text).contains("/images/fry/test.png")

    def it_rejects_unknown_templates(unknown_template):
        request, response = client.get(
            f"/images/{unknown_template.id}", allow_redirects=False
        )
        expect(response.status) == 404

    def it_creates_new_templates_when_debug(unknown_template, monkeypatch):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get(
            f"/images/{unknown_template.id}", allow_redirects=False
        )
        expect(response.status) == 501
        expect(response.text).contains("Template not fully implemented")

    def it_handles_sample_templates(monkeypatch):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get("/images/<sample>", allow_redirects=False)
        expect(response.status) == 501
        expect(response.text).contains("Replace '<sample>' in the URL")

    def it_handles_trailing_slashes():
        request, response = client.get("/images/fry/", allow_redirects=False)
        redirect = "/images/fry"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect


def describe_legacy_images(expect, client):
    @pytest.mark.parametrize("extension", ["png", "jpg"])
    def it_redirects_to_example_image(extension):
        request, response = client.get(f"/fry.{extension}", allow_redirects=False)
        redirect = f"/images/fry/not_sure_if_trolling/or_just_stupid.{extension}"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    @pytest.mark.parametrize("extension", ["png", "jpg"])
    def it_redirects_to_custom_image(extension):
        request, response = client.get(f"/fry/test.{extension}", allow_redirects=False)
        expect(response.status) == 302
        expect(response.headers["Location"]) == f"/images/fry/test.{extension}"


def describe_legacy_paths(client, expect, unknown_template):
    @pytest.mark.parametrize("suffix", ["", ".png", ".jpg"])
    def it_rejects_unknown_templates(suffix):
        request, response = client.get(f"/{unknown_template.id}{suffix}")
        expect(response.status) == 404

    @pytest.mark.parametrize("suffix", ["", ".png", ".jpg"])
    def it_rejects_unknown_templates_with_text(suffix):
        request, response = client.get(f"/{unknown_template.id}/test{suffix}")
        expect(response.status) == 404
