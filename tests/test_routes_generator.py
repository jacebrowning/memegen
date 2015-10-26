# pylint: disable=no-self-use


class TestGenerator:

    def test_get_generator(self, client):
        response = client.get("/generator")

        assert 200 == response.status_code
        assert 'text/html' == response.mimetype
        assert '<img src="' in response.get_data(as_text=True)
