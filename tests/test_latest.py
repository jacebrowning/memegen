# pylint: disable=unused-variable,expression-not-assigned

from expecter import expect


def describe_latest():

    def it_returns_filtered_images_by_default(client):
        response = client.get("/latest")

        expect(response.status_code) == 200
        expect(response.mimetype) == 'text/html'
        expect(response.get_data(as_text=True)).contains(
            'src="/latest1.jpg?filtered=True"')

    def it_returns_unfiltered_images_when_nsfw(client):
        response = client.get("/latest?nsfw=true")

        expect(response.status_code) == 200
        expect(response.mimetype) == 'text/html'
        expect(response.get_data(as_text=True)).contains(
            'src="/latest1.jpg?filtered=False"')
