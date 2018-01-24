# pylint: disable=unused-variable,expression-not-assigned

from expecter import expect

from .utils import load


def describe_root():

    def it_returns_links_and_metadata(client):
        status, data = load(client.get("/api/"))

        expect(status) == 200
        expect(data) == {
            'templates': "http://localhost/api/templates/",
            'fonts': "http://localhost/api/fonts/",
            'aliases': "http://localhost/api/aliases/",
            'search': "http://localhost/api/search/",
            'version': "5.3",
            'changes': "https://raw.githubusercontent.com/jacebrowning/memegen/master/CHANGELOG.md"
        }
