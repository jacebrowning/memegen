# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .utilities import load


def describe_get():

    def it_returns_a_list(client):
        status, data = load(client.get("/api/fonts/"))

        expect(status) == 200
        expect(data).contains('impact')


def describe_post():

    def new_fonts_are_created_using_github(client):
        status, data = load(client.post("/api/fonts/"))

        expect(status) == 403
        expect(data) == dict(
            message="https://raw.githubusercontent.com/jacebrowning/memegen/master/CONTRIBUTING.md"
        )
