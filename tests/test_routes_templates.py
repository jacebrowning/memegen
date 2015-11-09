# pylint: disable=no-self-use

from .conftest import load


class TestTemplates:

    def test_get(self, client):
        response = client.get("/templates/iw")

        assert 200 == response.status_code
        assert dict(
            name="Insanity Wolf",
            description="http://knowyourmeme.com/memes/insanity-wolf",
            aliases=['insanity', 'insanity-wolf', 'iw'],
            example="http://localhost/iw/does-testing/in-production",
        ) == load(response)

    def test_get_with_default(self, client):
        response = client.get("/templates/live")

        assert 200 == response.status_code
        assert dict(
            name="Do It Live!",
            description="http://knowyourmeme.com/memes/bill-oreilly-rant",
            aliases=["bill-o'reilly-rant", 'do-it-live', 'live', "o'reilly",
                     "o'reilly-rant"],
            example="http://localhost/live/_/do-it-live!",
        ) == load(response)

    def test_get_with_dash_in_key(self, client):
        response = client.get("/templates/awkward-awesome")

        assert 200 == response.status_code

    def test_get_all(self, client):
        response = client.get("/templates/")

        assert 200 == response.status_code
        data = load(response)
        assert "http://localhost/templates/iw" == data['Insanity Wolf']
        assert len(data) >= 20  # there should be many memes

    def test_get_redirects_when_text_is_provided(self, client):
        response = client.get("/templates/iw/top/bottom")

        assert 302 == response.status_code
        assert '<a href="/iw/top/bottom">' in load(response, as_json=False)

    def test_get_redirects_when_key_is_an_alias(self, client):
        response = client.get("/templates/insanity-wolf")

        assert 302 == response.status_code
        assert '<a href="/templates/iw">' in load(response, as_json=False)

    def test_post_returns_an_error(self, client):
        response = client.post("/templates/")

        assert 403 == response.status_code
        assert dict(
            message="http://github.com/jacebrowning/memegen/blob/master/CONTRIBUTING.md"
        ) == load(response)
