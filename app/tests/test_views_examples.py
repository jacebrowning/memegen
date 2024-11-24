import pytest

from .. import settings


def describe_examples():
    @pytest.mark.slow
    def it_displays_images(expect, client):
        request, response = client.get("/examples", timeout=15)
        expect(response.status) == 200
        expect(response.text.count("img")) > 100
        expect(response.text).excludes("setInterval")

    @pytest.mark.slow
    def it_can_enable_automatic_refresh(expect, client, monkeypatch):
        monkeypatch.setattr(settings, "DEBUG", True)
        request, response = client.get("/examples?debug=true", timeout=15)
        expect(response.status) == 200
        expect(response.text.count("img")) > 100
        expect(response.text).includes("setInterval")

    def describe_animated():
        @pytest.mark.slow
        def it_forces_webp(expect, client):
            request, response = client.get("/examples/animated", timeout=15)
            expect(response.status) == 200
            expect(response.text.count("webp")) > 100
            expect(response.text).excludes("setInterval")

    def describe_static():
        @pytest.mark.slow
        def it_forces_png(expect, client):
            request, response = client.get("/examples/static", timeout=15)
            expect(response.status) == 200
            expect(response.text.count("png")) > 100
            expect(response.text).excludes("setInterval")
