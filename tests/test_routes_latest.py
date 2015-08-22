# pylint: disable=no-self-use


class TestLatest:

    def test_get_latest(self, client):
        response = client.get("/latest")
        assert response.status_code == 200
        assert response.mimetype == 'text/html'
        assert '<img src="/latest.jpg"' in response.get_data(as_text=True)
