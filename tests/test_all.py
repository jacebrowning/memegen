from .conftest import load


class TestMeme:

    def test_get_jpg(self, client):
        response = client.get("/iw/hello/world.jpg")
        assert response.status_code == 200
        assert response.mimetype == 'image/jpeg'

    # TODO: add more image types

    # def test_get_jpeg(self, client):
    #     response = client.get("/iw/hello/world.jpeg")
    #     assert response.status_code == 200
    #     assert response.mimetype == 'image/jpeg'

    # def test_get_png(self, client):
    #     response = client.get("/iw/hello/world.png")
    #     assert response.status_code == 200
    #     assert response.mimetype == 'image/png'

    # def test_get_gif(self, client):
    #     response = client.get("/iw/hello/world.gif")
    #     assert response.status_code == 200
    #     assert response.mimetype == 'image/gif'


class TestLink:

    def test_get_links(self, client):
        response = client.get("/iw/hello/world")
        assert response.status_code == 200
        assert load(response) == dict(
            visible=dict(
                jpg="http://localhost/iw/hello/world.jpg",
            ),
            hidden=dict(
                jpg="http://localhost/aXcJaGVsbG8Jd29ybGQg.jpg",
            ),
        )
