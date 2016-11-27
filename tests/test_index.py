# pylint: disable=unused-variable,expression-not-assigned

from expecter import expect


def describe_generator():

    def it_returns_html(client):
        response = client.get("/")

        expect(response.status_code) == 200
        expect(response.mimetype) == 'text/html'
        expect(response.get_data(as_text=True)).contains("memegen.link")
