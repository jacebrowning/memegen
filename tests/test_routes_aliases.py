# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .conftest import load


def describe_get():

    def it_requires_a_name_to_return_aliases(client):
        response = client.get("/aliases/")

        assert 200 == response.status_code
        assert load(response) == []

    def it_redirects_with_param(client):
        response = client.get("/aliases/?name=foo")

        expect(response.status_code) == 302
        expect(load(response, as_json=False)).contains(
            '<a href="/aliases/foo">')

    def describe_filter():

        def with_single_match(client):
            response = client.get("/aliases/sad-biden")

            assert 200 == response.status_code
            assert {
                'sad-biden': {
                    'styles': [
                        'down',
                        'scowl',
                        'window',
                    ],
                    'template': "http://localhost/templates/sad-biden"
                }
            } == load(response)

        def with_many_matches(client):
            response = client.get("/aliases/votestakes")

            assert 200 == response.status_code
            assert len(load(response)) == 4
