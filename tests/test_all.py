from .conftest import load


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


class TestLink:

    def test_get_links(self, client):
        response = client.get("/iw/hello/world")
        assert response.status_code == 200
        assert dict(
            visible=dict(
                jpg="http://localhost/iw/hello/world.jpg",
            ),
            hidden=dict(
                jpg="http://localhost/aXcJaGVsbG8Jd29ybGQJ.jpg",
            ),
        ) == load(response)

    def test_get_links_redirect_hidden(self, client):
        response = client.get("/aXcJaGVsbG8Jd29ybGQJ")
        assert response.status_code == 302
        assert '<a href="/iw/hello/world">' in load(response, as_json=False)
