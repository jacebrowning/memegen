# pylint: disable=no-self-use
# pylint: disable=misplaced-comparison-constant


class TestLatest:

    def test_get_latest(self, client):
        response = client.get("/latest")

        assert 200 == response.status_code
        assert 'text/html' == response.mimetype
        assert '<img src="/latest.jpg"' in response.get_data(as_text=True)
