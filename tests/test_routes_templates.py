from .conftest import load


class TestTemplates:

    def test_get(self, client):
        response = client.get("/templates/iw")
        assert response.status_code == 200
        assert dict(
            description="http://knowyourmeme.com/memes/insanity-wolf",
            aliases=['insanity-wolf', 'insanity'],
            example="http://localhost/iw/hello/world",
        ) == load(response)

    def test_get_with_default(self, client):
        response = client.get("/templates/live")
        assert response.status_code == 200
        assert dict(
            description="http://knowyourmeme.com/memes/bill-oreilly-rant",
            aliases=['do-it-live'],
            example="http://localhost/live/_/do-it-live",
        ) == load(response)

    def test_get_all(self, client):
        response = client.get("/templates/")
        assert response.status_code == 200
        data = load(response)
        assert len(data) >= 3
        assert "http://localhost/templates/iw" == data['Insanity Wolf']

    def test_get_redirects_when_text_is_provided(self, client):
        response = client.get("/templates/iw/top/bottom")
        assert response.status_code == 302
        assert '<a href="/iw/top/bottom">' in load(response, as_json=False)

    def test_get_redirects_when_key_is_an_alias(self, client):
        response = client.get("/templates/insanity-wolf")
        assert response.status_code == 302
        assert '<a href="/templates/iw">' in load(response, as_json=False)
