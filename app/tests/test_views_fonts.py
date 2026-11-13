def describe_list():
    def describe_GET():
        def it_returns_all_fonts(expect, client):
            request, response = client.get("/fonts")
            expect(len(response.json)) == 9


def describe_detail():
    def describe_GET():
        def it_includes_filename(expect, client):
            request, response = client.get("/fonts/thick")
            expect(response.json) == {
                "id": "titilliumweb",
                "alias": "thick",
                "filename": "TitilliumWeb-Black.ttf",
                "_self": "http://localhost:5000/fonts/titilliumweb",
            }

        def it_includes_the_arabic_font(expect, client):
            request, response = client.get("/fonts/ar")
            expect(response.json) == {
                "id": "lalezar",
                "alias": "ar",
                "filename": "Lalezar-Regular.ttf",
                "_self": "http://localhost:5000/fonts/lalezar",
            }
