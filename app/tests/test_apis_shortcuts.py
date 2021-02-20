import pytest

from .. import settings


def describe_image_redirects():
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
        request, response = client.get("/images/fry/1 2%0A3.jpg", allow_redirects=False)
        redirect = "/images/fry/1_2~n3.jpg"
        expect(response.status) == 301
        expect(response.headers["Location"]) == redirect


def describe_path_redirects():
    def it_redirects_to_example_image_when_no_extension(expect, client):
        request, response = client.get("/images/fry", allow_redirects=False)
        redirect = "/images/fry/not_sure_if_trolling/or_just_stupid"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    def it_redirects_to_custom_image_when_no_extension(expect, client):
        request, response = client.get("/images/fry/one%3F/two", allow_redirects=False)
        expect(response.status) == 302
        expect(response.headers["Location"]) == "/images/fry/one~q/two.png"

    def it_returns_gallery_view_when_debug(expect, client, monkeypatch):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get("/images/fry/test")
        expect(response.text).contains("/images/fry/test.png")

    def it_rejects_unknown_templates(expect, client, unknown_template):
        request, response = client.get(
            f"/images/{unknown_template.id}", allow_redirects=False
        )
        expect(response.status) == 404

    def it_creates_new_templates_when_debug(
        expect, client, unknown_template, monkeypatch
    ):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get(
            f"/images/{unknown_template.id}", allow_redirects=False
        )
        expect(response.status) == 501

    def it_handles_sample_templates(expect, client, monkeypatch):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get(f"/images/<sample>", allow_redirects=False)
        expect(response.status) == 501


def describe_legacy_images():
    @pytest.mark.parametrize("ext", ["png", "jpg"])
    def it_redirects_to_example_image(expect, client, ext):
        request, response = client.get(f"/fry.{ext}", allow_redirects=False)
        redirect = f"/images/fry/not_sure_if_trolling/or_just_stupid.{ext}"
        expect(response.status) == 302
        expect(response.headers["Location"]) == redirect

    @pytest.mark.parametrize("ext", ["png", "jpg"])
    def it_redirects_to_custom_image(expect, client, ext):
        request, response = client.get(f"/fry/test.{ext}", allow_redirects=False)
        expect(response.status) == 302
        expect(response.headers["Location"]) == f"/images/fry/test.{ext}"


def describe_legacy_paths():
    @pytest.mark.parametrize("suffix", ["", ".png", ".jpg"])
    def it_rejects_unknown_templates(expect, client, unknown_template, suffix):
        request, response = client.get(f"/{unknown_template.id}{suffix}")
        expect(response.status) == 404

    @pytest.mark.parametrize("suffix", ["", ".png", ".jpg"])
    def it_rejects_unknown_templates_with_text(
        expect, client, unknown_template, suffix
    ):
        request, response = client.get(f"/{unknown_template.id}/test{suffix}")
        expect(response.status) == 404


def describe_legacy_params():
    def it_accepts_alt_for_template(expect, client):
        request, response = client.get(
            "/images/custom/test.png?alt=https://www.gstatic.com/webp/gallery/3.jpg"
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
