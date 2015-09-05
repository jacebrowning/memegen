# pylint: disable=no-self-use


class TestOverview:

    def test_get_overview(self, client):
        response = client.get("/overview")

        assert 200 == response.status_code
        assert 'text/html' == response.mimetype
        assert '<img src="' in response.get_data(as_text=True)
