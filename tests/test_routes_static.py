# pylint: disable=no-self-use

from .conftest import load


class TestStatic:

    def test_get_index(self, client):
        response = client.get("/")

        assert 200 == response.status_code
        assert 'href="/api"' in load(response, as_json=False)
