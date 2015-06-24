from .conftest import load

GITHUB_BASE = "http://github.com/jacebrowning/memegen/blob/master/"


class TestRoot:

    def test_get_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert dict(
            templates="http://localhost/templates/",
            source=GITHUB_BASE,
            contributing=GITHUB_BASE + "CONTRIBUTING.md",
        ) == load(response)
