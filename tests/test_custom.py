# pylint: disable=unused-variable,expression-not-assigned,line-too-long

from expecter import expect


def describe_custom():

    def it_selects_image_from_query_param(client):
        response = client.get("/custom?image=http://www.gstatic.com/webp/gallery/2.jpg")

        expect(response.status_code) == 200
        expect(response.mimetype) == 'text/html'

        html = response.get_data(as_text=True)

        expect(html).contains("$('#meme-font').val('titilliumweb-black');")
        expect(html).contains("$('#meme-background').val('http://www.gstatic.com/webp/gallery/2.jpg');")

    def it_selects_font_from_query_param(client):
        response = client.get("/custom?font=impact")

        expect(response.status_code) == 200
        expect(response.mimetype) == 'text/html'

        html = response.get_data(as_text=True)

        expect(html).contains("$('#meme-font').val('impact');")
        expect(html).contains("$('#meme-background').val('https://raw.githubusercontent.com/jacebrowning/memegen/main/memegen/static/images/missing.png');")
