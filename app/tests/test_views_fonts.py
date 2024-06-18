def describe_list():
    def describe_GET():
        def it_returns_all_fonts(expect, client):
            request, response = client.get("/fonts")
            expect(len(response.json)) == 7


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
