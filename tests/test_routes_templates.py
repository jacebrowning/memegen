# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .conftest import load


def describe_get():

    def when_default_text(client):
        response = client.get("/templates/iw")

        assert 200 == response.status_code
        assert dict(
            name="Insanity Wolf",
            description="http://knowyourmeme.com/memes/insanity-wolf",
            aliases=['insanity', 'insanity-wolf', 'iw'],
            styles=[],
            example="http://localhost/iw/does-testing/in-production",
        ) == load(response)

    def when_no_default_text(client):
        response = client.get("/templates/keanu")

        assert 200 == response.status_code
        assert "http://localhost/keanu/your-text/goes-here" == \
            load(response)['example']

    def when_alternate_sytles_available(client):
        response = client.get("/templates/sad-biden")

        assert 200 == response.status_code
        assert ['down', 'scowl', 'window'] == load(response)['styles']

    def when_dashes_in_key(client):
        response = client.get("/templates/awkward-awesome")

        assert 200 == response.status_code

    def it_returns_list_when_no_key(client):
        response = client.get("/templates/")

        assert 200 == response.status_code
        data = load(response)
        assert "http://localhost/templates/iw" == data['Insanity Wolf']
        assert len(data) >= 20  # there should be many memes

    def it_redirects_when_text_is_provided(client):
        response = client.get("/templates/iw/top/bottom")

        assert 302 == response.status_code
        assert '<a href="/iw/top/bottom">' in load(response, as_json=False)

    def it_redirects_when_key_is_an_alias(client):
        response = client.get("/templates/insanity-wolf")

        assert 302 == response.status_code
        assert '<a href="/templates/iw">' in load(response, as_json=False)


def describe_post():

    def new_templates_are_created_using_github(client):
        response = client.post("/templates/")

        assert 403 == response.status_code
        assert dict(
            message="https://raw.githubusercontent.com/jacebrowning/memegen/master/CONTRIBUTING.md"
        ) == load(response)

    def can_create_a_new_meme(client):
        params = {'top': "foo", 'bottom': "bar"}
        response = client.post("/templates/fry", data=params)

        expect(response.status_code) == 303
        expect(load(response, as_json=False)).contains(
            '<a href="/fry/foo/bar.jpg">'
        )
