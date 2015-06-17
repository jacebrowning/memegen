from .conftest import load


class TestRoot:

    def test_get_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert dict(
            templates="http://localhost/templates/",
        ) == load(response)


class TestTemplates:

    def test_get_templates(self, client):
        response = client.get("/templates/")
        assert response.status_code == 200
        data = load(response)
        assert len(data) > 0  # TODO: check for a minimum number of memes
        assert "http://localhost/templates/iw" == data['Insanity Wolf']

    def test_get_template(self, client):
        response = client.get("/templates/iw")
        assert response.status_code == 200
        assert dict(
            example="http://localhost/iw/hello/world",
        ) == load(response)


class TestLink:

    def test_get_links(self, client):
        response = client.get("/iw/hello/world")
        assert response.status_code == 200
        assert dict(
            visible=dict(
                JPG="http://localhost/iw/hello/world.jpg",
            ),
            hidden=dict(
                JPG="http://localhost/aXcJaGVsbG8Jd29ybGQJ.jpg",
            ),
        ) == load(response)

    def test_get_links_redirect_hidden(self, client):
        response = client.get("/aXcJaGVsbG8Jd29ybGQJ")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)


class TestMeme:

    def test_get_visible_jpg(self, client):
        response = client.get("/iw/hello/world.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'

    # TODO: add more image types

    # def test_get_visible_jpeg(self, client):
    #     response = client.get("/iw/hello/world.jpeg")
    #     assert response.status_code == 200
    #     assert response.mimetype == 'image/jpeg'

    # def test_get_visible_png(self, client):
    #     response = client.get("/iw/hello/world.png")
    #     assert response.status_code == 200
    #     assert response.mimetype == 'image/png'

    # def test_get_visible_gif(self, client):
    #     response = client.get("/iw/hello/world.gif")
    #     assert response.status_code == 200
    #     assert response.mimetype == 'image/gif'

    def test_get_hidden_jpg(self, client):
        response = client.get("/aXcJaGVsbG8Jd29ybGQJ.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'
