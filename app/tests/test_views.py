def describe_index():
    def describe_GET():
        def it_displays_sample_images(expect, client):
            request, response = client.get("/")
            expect(response.status) == 200
            expect(response.text.count("img")) > 100
