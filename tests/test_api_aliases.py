# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .utils import load


def describe_get():

    def it_redirects_with_param(client):
        status, data = load(client.get("/api/aliases/?name=foo"))

        expect(status) == 302
        expect(data).contains('<a href="/api/aliases/foo">')

    def describe_filter():

        def with_single_match(client):
            status, data = load(client.get("/api/aliases/sad-biden"))

            expect(status) == 200
            expect(data) == {
                'sad-biden': {
                    'styles': [
                        'down',
                        'scowl',
                        'window',
                    ],
                    'template': "http://localhost/api/templates/sad-biden"
                }
            }

        def with_many_matches(client):
            status, data = load(client.get("/api/aliases/votestakes"))

            expect(status) == 200
            expect(len(data)) == 5
