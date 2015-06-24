from .conftest import load


class TestLinks:

    def test_get(self, client):
        response = client.get("/iw/hello/world")
        assert response.status_code == 200
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
        assert response.status_code == 200
        assert dict(
            visible="http://localhost/iw/hello.jpg",
            masked="http://localhost/_aXcJaGVsbG8J.jpg",
        ) == load(response, key='direct')

    def test_get_with_bottom_only(self, client):
        response = client.get("/iw/_/hello")
        assert response.status_code == 200
        assert dict(
            visible="http://localhost/iw/_/hello.jpg",
            masked="http://localhost/_aXcJXy9oZWxsbwkJ.jpg",
        ) == load(response, key='direct')

    def test_get_redirects_to_dashes(self, client):
        response = client.get("/iw/HelloThere_World/How-areYOU")
        assert response.status_code == 302
        assert '<a href="/iw/hello-there-world/how-are-you">' in \
            load(response, as_json=False)

    def test_get_redirects_when_masked(self, client):
        response = client.get("/_aXcJaGVsbG8vd29ybGQJ")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)

    def test_get_redirects_when_masked_with_1_line(self, client):
        response = client.get("/_aXcJaGVsbG8J")
        assert response.status_code == 302
        assert '<a href="/iw/hello">' in load(response, as_json=False)

    def test_get_redirects_to_default(self, client):
        response = client.get("/live")
        assert response.status_code == 302
        assert '<a href="/live/_/do-it-live">' in load(response, as_json=False)

    def test_get_redirects_when_alias(self, client):
        response = client.get("/insanity-wolf")
        assert response.status_code == 302
        assert '<a href="/iw">' in load(response, as_json=False)

    def test_get_redirects_when_alias_with_text(self, client):
        response = client.get("/insanity-wolf/hello/world")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)
