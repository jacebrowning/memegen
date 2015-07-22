from .conftest import load


class TestStatic:

    def test_get_index(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert 'href="/api"' in load(response, as_json=False)
