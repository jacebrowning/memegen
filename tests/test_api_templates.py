# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .conftest import load


def describe_get():

    def it_returns_template_info(client):
        response = client.get("/api/templates/iw")

        assert 200 == response.status_code
        assert dict(
            name="Insanity Wolf",
            description="http://knowyourmeme.com/memes/insanity-wolf",
            aliases=['insanity', 'insanity-wolf', 'iw'],
            styles=[],
            example="http://localhost/api/templates/iw/does-testing/in-production",
        ) == load(response)

    def when_no_default_text(client):
        response = client.get("/api/templates/keanu")

        assert 200 == response.status_code
        assert "http://localhost/api/templates/keanu/your-text/goes-here" == \
            load(response)['example']

    def when_alternate_sytles_available(client):
        response = client.get("/api/templates/sad-biden")

        assert 200 == response.status_code
        assert ['down', 'scowl', 'window'] == load(response)['styles']

    def when_dashes_in_key(client):
        response = client.get("/api/templates/awkward-awesome")

        assert 200 == response.status_code

    def it_returns_list_when_no_key(client):
        response = client.get("/api/templates/")

        assert 200 == response.status_code
        data = load(response)
        assert "http://localhost/api/templates/iw" == data['Insanity Wolf']
        assert len(data) >= 20  # there should be many memes

    def it_redirects_when_key_is_an_alias(client):
        response = client.get("/api/templates/insanity-wolf")

        assert 302 == response.status_code
        assert '<a href="/api/templates/iw">' in load(response, as_json=False)

    def old_api_is_still_supported_via_redirect(client):
        response = client.get("/templates/")

        assert 302 == response.status_code
        assert '<a href="/api/templates/">' in load(response, as_json=False)


def describe_post():

    def it_requies_an_existing_template(client):
        response = client.post("/api/templates/")

        assert 403 == response.status_code
        assert dict(
            message="https://raw.githubusercontent.com/jacebrowning/memegen/master/CONTRIBUTING.md"
        ) == load(response)

    def it_can_create_a_new_meme(client):
        params = {'top': "foo", 'bottom': "bar"}
        response = client.post("/api/templates/fry", data=params)

        expect(response.status_code) == 303
        expect(load(response, as_json=False)).contains(
            '<a href="/fry/foo/bar.jpg">'
        )

    def it_escapes_special_characters(client):
        params = {'top': "#special characters?", 'bottom': "underscore_ dash-"}
        response = client.post("/api/templates/fry", data=params)

        expect(response.status_code) == 303
        expect(load(response, as_json=False)).contains(
            '<a href="/fry/~hspecial-characters~q/underscore__-dash--.jpg">'
        )

    def it_supports_top_only(client):
        params = {'top': "foo"}
        response = client.post("/api/templates/fry", data=params)

        expect(response.status_code) == 303
        expect(load(response, as_json=False)).contains(
            '<a href="/fry/foo.jpg">'
        )

    def it_supports_bottom_only(client):
        params = {'bottom': "bar"}
        response = client.post("/api/templates/fry", data=params)

        expect(response.status_code) == 303
        expect(load(response, as_json=False)).contains(
            '<a href="/fry/_/bar.jpg">'
        )
