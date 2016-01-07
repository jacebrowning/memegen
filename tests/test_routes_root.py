# pylint: disable=unused-variable,misplaced-comparison-constant

from .conftest import load


def describe_root():

    def it_returns_links_and_metadata(client):
        response = client.get("/api")

        assert 200 == response.status_code
        assert dict(
            templates="http://localhost/templates/",
            aliases="http://localhost/aliases/",
            version="2.0",
            changes="https://raw.githubusercontent.com/jacebrowning/memegen/master/CHANGES.md"
        ) == load(response)
