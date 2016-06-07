# pylint: disable=unused-variable,expression-not-assigned

from expecter import expect

from .conftest import load


def describe_root():

    def it_returns_links_and_metadata(client, monkeypatch):
        monkeypatch.setenv('DEPLOY_DATE', "today")

        response = client.get("/api")

        expect(response.status_code) == 200
        expect(load(response)) == {
            'templates': "http://localhost/templates/",
            'aliases': "http://localhost/aliases/",
            'magic': "http://localhost/magic/",
            'version': "2.1",
            'date': "today",
            'changes': "https://raw.githubusercontent.com/jacebrowning/memegen/master/CHANGELOG.md"
        }
