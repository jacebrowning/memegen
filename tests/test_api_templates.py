# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .utils import load


def describe_get():

    def it_returns_template_info(client):
        status, data = load(client.get("/api/templates/iw"))

        expect(status) == 200
        expect(data) == {
            'name': "Insanity Wolf",
            'description': "http://knowyourmeme.com/memes/insanity-wolf",
            'aliases': ['insanity', 'insanity-wolf', 'iw'],
            'styles': [],
            'example': "http://localhost/api/templates/iw/does_testing/in_production",
        }

    def when_no_default_text(client):
        status, data = load(client.get("/api/templates/keanu"))

        expect(status) == 200
        expect(data['example']) == "http://localhost/api/templates/keanu/your_text/goes_here"

    def when_alternate_sytles_available(client):
        status, data = load(client.get("/api/templates/sad-biden"))

        expect(status) == 200
        expect(data['styles']) == ['down', 'scowl', 'window']

    def when_dashes_in_key(client):
        status, data = load(client.get("/api/templates/awkward-awesome"))

        expect(status) == 200

    def it_returns_list_when_no_key(client):
        status, data = load(client.get("/api/templates/"))

        expect(status) == 200
        expect(data['Insanity Wolf']) == "http://localhost/api/templates/iw"
        expect(len(data)) >= 20  # there should be many memes

    def it_redirects_when_key_is_an_alias(client):
        status, data = load(client.get("/api/templates/insanity-wolf"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/iw">')

    def old_api_is_still_supported_via_redirect(client):
        status, data = load(client.get("/templates/"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/">')


def describe_post():

    def it_requies_an_existing_template(client):
        status, data = load(client.post("/api/templates/"))

        expect(status) == 403
        expect(data) == {
            'message': "https://raw.githubusercontent.com/jacebrowning/memegen/master/CONTRIBUTING.md"
        }

    def it_can_create_a_new_meme(client):
        params = {'top': "foo", 'bottom': "bar"}
        status, data = load(client.post("/api/templates/fry", data=params))

        expect(status) == 303
        expect(data).contains(
            '<a href="http://localhost/fry/foo/bar.jpg">'
        )

    def it_escapes_special_characters(client):
        params = {'top': "#special characters?", 'bottom': "underscore_ dash-"}
        status, data = load(client.post("/api/templates/fry", data=params))

        expect(status) == 303
        expect(data).contains(
            '<a href="http://localhost/fry/~hspecial_characters~q/underscore___dash--.jpg">'
        )

    def it_supports_top_only(client):
        params = {'top': "foo"}
        status, data = load(client.post("/api/templates/fry", data=params))

        expect(status) == 303
        expect(data).contains(
            '<a href="http://localhost/fry/foo.jpg">'
        )

    def it_supports_bottom_only(client):
        params = {'bottom': "bar"}
        status, data = load(client.post("/api/templates/fry", data=params))

        expect(status) == 303
        expect(data).contains(
            '<a href="http://localhost/fry/_/bar.jpg">'
        )

    def it_supports_no_text(client):
        params = {}
        status, data = load(client.post("/api/templates/fry", data=params))

        expect(status) == 303
        expect(data).contains(
            '<a href="http://localhost/fry/_.jpg">'
        )

    def it_can_return_json_instead_of_redirecting(client):
        params = {'top': "foo", 'bottom': "bar", 'redirect': False}
        status, data = load(client.post("/api/templates/fry", data=params))

        expect(status) == 200
        expect(data) == {
            'href': "http://localhost/fry/foo/bar.jpg"
        }
