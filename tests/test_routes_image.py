# pylint: disable=no-self-use

import os

from .conftest import load

TESTS = os.path.dirname(__file__)
ROOT = os.path.dirname(TESTS)


class TestImage:

    def test_get_visible_jpg(self, client):
        path = os.path.join(ROOT, 'data', 'images', 'iw', 'hello', 'world.jpg')
        if os.path.exists(path):
            os.remove(path)

        response = client.get("/iw/hello/world.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'

        assert os.path.isfile(path)

    def test_get_visible_jpg_1_line(self, client):
        response = client.get("/iw/hello.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'

    def test_get_hidden_jpg(self, client):
        response = client.get("/_aXcJaGVsbG8vd29ybGQJ.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'

    def test_redirects_to_dashes(self, client):
        response = client.get("/iw/HelloThere_World/How-areYOU.jpg")
        assert response.status_code == 302
        assert '<a href="/iw/hello-there-world/how-are-you.jpg">' in \
            load(response, as_json=False)

    def test_get_unknown_template(self, client):
        response = client.get("/make/sudo/give.me.jpg")
        assert response.status_code == 404

    def test_get_redirects_to_default(self, client):
        response = client.get("/live.jpg")
        assert response.status_code == 302
        assert '<a href="/live/_/do-it-live%7Ee.jpg">' in \
            load(response, as_json=False)

    def test_get_redirects_when_alias(self, client):
        response = client.get("/insanity-wolf/hello/world.jpg")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world.jpg">' in \
            load(response, as_json=False)

    def test_get_redirects_when_jpeg_without_text(self, client):
        response = client.get("/iw.jpeg")
        assert response.status_code == 302
        assert '<a href="/iw.jpg">' in \
            load(response, as_json=False)

    def test_get_redirects_when_jpeg_with_text(self, client):
        response = client.get("/iw/hello/world.jpeg")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world.jpg">' in \
            load(response, as_json=False)
