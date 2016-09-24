# pylint: disable=unused-variable,expression-not-assigned

from expecter import expect

from .conftest import load


def describe_pattern():

    def it_returns_matches(client):
        response = client.get("/api/magic/do-all-the-things")

        expect(response.status_code) == 200
        expect(load(response)) == [
            {
                'link': "http://localhost/api/templates/xy/do/all-the-things",
                'ratio': 0.94,
            },
        ]

    def it_returns_an_empty_list_when_no_matches(client):
        response = client.get("/api/magic/_")

        expect(response.status_code) == 200
        expect(load(response)) == []

    def it_returns_an_empty_list_for_missing_patterns(client):
        response = client.get("/api/magic/")

        expect(response.status_code) == 200
        expect(load(response)) == []

    def it_redirects_to_use_dashes(client):
        response = client.get("/api/magic/do all the things")

        expect(response.status_code) == 302
        expect(load(response, as_json=False)).contains(
            '<a href="/api/magic/do-all-the-things">')


def describe_image():

    def it_redirects_to_an_image(client):
        response = client.get("/api/magic/do all the things.jpg")

        expect(response.status_code) == 302
        expect(load(response, as_json=False)).contains(
            '<a href="/xy/do/all-the-things.jpg">')

    def even_when_no_match(client):
        response = client.get("/api/magic/_.jpg")

        expect(response.status_code) == 302
        expect(load(response, as_json=False)).contains(
            '<a href="/unknown/_.jpg">')
