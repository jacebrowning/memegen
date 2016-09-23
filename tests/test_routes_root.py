# pylint: disable=unused-variable,expression-not-assigned

from expecter import expect

from .utilities import load


def describe_root():

    def it_returns_links_and_metadata(client):
        status, data = load(client.get("/api"))

        expect(status) == 200
        expect(data) == {
            'templates': "http://localhost/templates/",
            'fonts': "http://localhost/api/fonts/",
            'aliases': "http://localhost/aliases/",
            'magic': "http://localhost/magic/",
            'version': "3.0",
            'changes': "https://raw.githubusercontent.com/jacebrowning/memegen/master/CHANGELOG.md"
        }
