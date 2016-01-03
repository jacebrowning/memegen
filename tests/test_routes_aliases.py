# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from .conftest import load


def describe_get():

    def it_returns_all_aliases(client):
        response = client.get("/aliases/")

        assert 200 == response.status_code
        assert len(load(response)) > 200

    def describe_filter():

        def with_single_match(client):
            response = client.get("/aliases/?name=sad-biden")

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
            response = client.get("/aliases/?name=votestakes")

            assert 200 == response.status_code
            assert len(load(response)) == 3
