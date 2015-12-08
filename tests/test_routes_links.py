# pylint: disable=no-self-use
# pylint: disable=misplaced-comparison-constant

from .conftest import load


class TestLinks:

    def test_get(self, client):
        response = client.get("/iw/hello/world")

        assert 200 == response.status_code
        assert dict(
            direct=dict(
                visible="http://localhost/iw/hello/world.jpg",
                masked="http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg",
            ),
            markdown=dict(
                visible="![iw](http://localhost/iw/hello/world.jpg)",
                masked="![iw](http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg)",
            ),
        ) == load(response)

    def test_get_with_top_only(self, client):
        response = client.get("/iw/hello")

        assert 200 == response.status_code
        assert dict(
            visible="http://localhost/iw/hello.jpg",
            masked="http://localhost/_aXcJaGVsbG8J.jpg",
        ) == load(response, key='direct')

    def test_get_with_bottom_only(self, client):
        response = client.get("/iw/_/hello")

        assert 200 == response.status_code
        assert dict(
            visible="http://localhost/iw/_/hello.jpg",
            masked="http://localhost/_aXcJXy9oZWxsbwkJ.jpg",
        ) == load(response, key='direct')

    def test_get_redirects_to_dashes(self, client):
        response = client.get("/iw/HelloThere_World/How-areYOU")

        assert 302 == response.status_code
        assert '<a href="/iw/hello-there-world/how-are-you">' in \
            load(response, as_json=False)

    def test_get_redirects_when_masked(self, client):
        response = client.get("/_aXcJaGVsbG8vd29ybGQJ")

        assert 302 == response.status_code
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)

    def test_get_redirects_when_masked_with_1_line(self, client):
        response = client.get("/_aXcJaGVsbG8J")

        assert 302 == response.status_code
        assert '<a href="/iw/hello">' in load(response, as_json=False)

    def test_get_without_extension_redirects_to_template(self, client):
        response = client.get("/live")

        assert 302 == response.status_code
        assert '<a href="/templates/live">' in \
            load(response, as_json=False)

    def test_get_redirects_when_alias(self, client):
        response = client.get("/insanity-wolf")

        assert 302 == response.status_code
        assert '<a href="/templates/iw">' in load(response, as_json=False)

    def test_get_redirects_when_alias_with_text(self, client):
        response = client.get("/insanity-wolf/hello/world")

        assert 302 == response.status_code
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)
