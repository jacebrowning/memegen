# pylint: disable=no-self-use
# pylint: disable=misplaced-comparison-constant

from .conftest import load

GITHUB_BASE = "http://github.com/jacebrowning/memegen/"


class TestRoot:

    def test_get_root(self, client):
        response = client.get("/api")

        assert 200 == response.status_code
        assert dict(
            templates="http://localhost/templates/",
            version="1",
        ) == load(response)
