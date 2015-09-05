# pylint: disable=no-self-use

import os

from .conftest import load

TESTS = os.path.dirname(__file__)
ROOT = os.path.dirname(TESTS)
LATEST = os.path.join(ROOT, "data", "images", "latest.jpg")


class TestImage:

    def test_get_visible_jpg(self, client):
        path = os.path.join(ROOT, 'data', 'images', 'iw', 'hello', 'world.jpg')
        if os.path.exists(path):
            os.remove(path)

        response = client.get("/iw/hello/world.jpg")

        assert 200 == response.status_code
        assert 'image/jpeg' == response.mimetype
        assert os.path.isfile(path)

    def test_get_visible_jpg_with_only_1_line(self, client):
        response = client.get("/iw/hello.jpg")

        assert 200 == response.status_code
        assert 'image/jpeg' == response.mimetype

    def test_get_visible_jpg_with_lots_of_text(self, client):
        top = "-".join(["hello"] * 20)
        bottom = "-".join(["hello"] * 20)
        response = client.get("/iw/" + top + "/" + bottom + ".jpg")

        assert 200 == response.status_code
        assert 'image/jpeg' == response.mimetype

    def test_get_hidden_jpg(self, client):
        response = client.get("/_aXcJaGVsbG8vd29ybGQJ.jpg")

        assert 200 == response.status_code
        assert 'image/jpeg' == response.mimetype

    def test_redirects_to_dashes(self, client):
        response = client.get("/iw/HelloThere_World/How-areYOU.jpg")

        assert 302 == response.status_code
        assert '<a href="/iw/hello-there-world/how-are-you.jpg">' in \
            load(response, as_json=False)

    def test_get_unknown_template(self, client):
        response = client.get("/make/sudo/give.me.jpg")

        assert 404 == response.status_code

    def test_get_redirects_to_default(self, client):
        response = client.get("/live.jpg")

        assert 302 == response.status_code
        assert '<a href="/live/_/do-it-live!.jpg">' in \
            load(response, as_json=False)

    def test_get_redirects_when_alias(self, client):
        response = client.get("/insanity-wolf/hello/world.jpg")

        assert 302 == response.status_code
        assert '<a href="/iw/hello/world.jpg">' in \
            load(response, as_json=False)

    def test_get_redirects_when_jpeg_without_text(self, client):
        response = client.get("/iw.jpeg")

        assert 302 == response.status_code
        assert '<a href="/iw.jpg">' in \
            load(response, as_json=False)

    def test_get_redirects_when_jpeg_with_text(self, client):
        response = client.get("/iw/hello/world.jpeg")

        assert 302 == response.status_code
        assert '<a href="/iw/hello/world.jpg">' in \
            load(response, as_json=False)

    def test_get_latest(self, client):
        open(LATEST, 'w').close()  # force the file to exist
        response = client.get("/latest.jpg")

        assert 200 == response.status_code
        assert 'image/jpeg' == response.mimetype

    def test_get_latest_when_no_images(self, client):
        try:
            os.remove(LATEST)
        except FileNotFoundError:
            pass

        response = client.get("/latest.jpg")

        assert 302 == response.status_code
        assert '<a href="/fry/_.jpg">' in load(response, as_json=False)
