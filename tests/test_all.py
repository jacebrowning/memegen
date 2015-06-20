from .conftest import load


class TestRoot:

    def test_get_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert dict(
            templates="http://localhost/templates/",
        ) == load(response)


class TestTemplates:

    def test_get(self, client):
        response = client.get("/templates/iw")
        assert response.status_code == 200
        assert dict(
            example="http://localhost/iw/hello/world",
        ) == load(response)

    def test_get_with_default(self, client):
        response = client.get("/templates/live")
        assert response.status_code == 200
        assert dict(
            example="http://localhost/live/_/do-it-live",
        ) == load(response)

    def test_get_all(self, client):
        response = client.get("/templates/")
        assert response.status_code == 200
        data = load(response)
        assert len(data) >= 3
        assert "http://localhost/templates/iw" == data['Insanity Wolf']

    def test_get_redirects_when_text_is_provided(self, client):
        response = client.get("/templates/iw/top/bottom")
        assert response.status_code == 302
        assert '<a href="/iw/top/bottom">' in load(response, as_json=False)

    def test_get_redirects_when_key_is_an_alias(self, client):
        response = client.get("/templates/insanity-wolf")
        assert response.status_code == 302
        assert '<a href="/templates/iw">' in load(response, as_json=False)


class TestLinks:

    def test_get(self, client):
        response = client.get("/iw/hello/world")
        assert response.status_code == 200
        assert dict(
            visible="http://localhost/iw/hello/world.jpg",
            hidden="http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg",
        ) == load(response)

    def test_get_with_top_only(self, client):
        response = client.get("/iw/hello")
        assert response.status_code == 200
        assert dict(
            visible="http://localhost/iw/hello.jpg",
            hidden="http://localhost/_aXcJaGVsbG8J.jpg",
        ) == load(response)

    def test_get_with_bottom_only(self, client):
        response = client.get("/iw/_/hello")
        assert response.status_code == 200
        assert dict(
            visible="http://localhost/iw/_/hello.jpg",
            hidden="http://localhost/_aXcJXy9oZWxsbwkJ.jpg",
        ) == load(response)

    def test_get_redirects_to_dashes(self, client):
        response = client.get("/iw/HelloThere_World/How-areYOU")
        assert response.status_code == 302
        assert '<a href="/iw/hello-there-world/how-are-you">' in \
            load(response, as_json=False)

    def test_get_redirects_when_hidden(self, client):
        response = client.get("/_aXcJaGVsbG8vd29ybGQJ")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)

    def test_get_redirects_when_hidden_with_1_line(self, client):
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


class TestImage:

    def test_get_visible_jpg(self, client):
        response = client.get("/iw/hello/world.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'

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
        assert '<a href="/live/_/do-it-live.jpg">' in load(response, as_json=False)

    def test_get_redirects_when_alias(self, client):
        response = client.get("/insanity-wolf/hello/world.jpg")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world.jpg">' in load(response, as_json=False)
