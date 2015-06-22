from .conftest import load


class TestRoot:

    def test_get_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert dict(
            templates="http://localhost/templates/",
        ) == load(response)
