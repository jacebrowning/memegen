from .conftest import load

GITHUB_BASE = "http://github.com/jacebrowning/memegen/"


class TestRoot:

    def test_get_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert dict(
            templates="http://localhost/templates/",
            source=GITHUB_BASE,
            contributing=GITHUB_BASE + "blob/master/CONTRIBUTING.md",
        ) == load(response)
