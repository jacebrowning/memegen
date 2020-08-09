import json


def describe_root():
    def describe_GET():
        def it_returns_all_routes(expect, client):
            request, response = client.get("/api")
            expect(response.status) == 200
            expect(response.json) == {
                "templates": "http://localhost:5000/api/templates",
                "images": "http://localhost:5000/api/images",
                "docs": "http://localhost:5000/api/docs",
            }


def describe_template_list():
    def describe_GET():
        def it_returns_all_templates(expect, client):
            request, response = client.get("/api/templates")
            expect(response.status) == 200


def describe_template_detail():
    def describe_GET():
        def it_returns_sample_images(expect, client):
            request, response = client.get("/api/templates/iw")
            expect(response.status) == 200
            expect(response.json) == {
                "name": "Insanity Wolf",
                "styles": [],
                "blank": "http://localhost:5000/api/images/iw.png",
                "sample": "http://localhost:5000/api/images/iw/does_testing/in_production.png",
                "source": "http://knowyourmeme.com/memes/insanity-wolf",
                "_self": "http://localhost:5000/api/templates/iw",
            }

        def it_returns_404_when_missing(expect, client):
            request, response = client.get("/api/templates/foobar")
            expect(response.status) == 404


def describe_image_list():
    def describe_GET():
        def it_returns_sample_image_urls(expect, client):
            request, response = client.get("/api/images")
            expect(response.status) == 200
            expect(response.json).contains(
                {
                    "url": "http://localhost:5000/api/images/iw/does_testing/in_production.png"
                }
            )

    def describe_POST():
        def it_returns_an_image_url(expect, client):
            data = {"key": "iw", "lines": ["foo", "bar"]}
            request, response = client.post("/api/images", data=json.dumps(data))
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/api/images/iw/foo/bar.png"
            }


def describe_image_detail():
    def describe_GET():
        def it_returns_an_image(expect, client):
            request, response = client.get("/api/images/fry/test.png")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

            request, response = client.get("/api/images/fry/test.jpg")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/jpeg"

        def it_supports_custom_templates(expect, client):
            request, response = client.get(
                "/api/images/custom/test.png"
                "?alt=https://www.gstatic.com/webp/gallery/3.jpg"
            )
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

        def it_requires_an_image_with_custom_templates(expect, client):
            request, response = client.get("/api/images/custom/test.png")
            expect(response.status) == 422
            expect(response.headers["content-type"]) == "image/png"

        def it_returns_blank_templates_when_no_slug(expect, client):
            request, response = client.get("/api/images/fry.png")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

            request, response = client.get("/api/images/fry.jpg")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/jpeg"

        def it_handles_unknown_templates(expect, client):
            request, response = client.get("/api/images/unknown/test.png")
            expect(response.status) == 404
            expect(response.headers["content-type"]) == "image/png"

        def it_supports_direct_image_access_for_legacy_support(expect, client):
            request, response = client.get("/fry.png")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

            request, response = client.get("/fry.jpg")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/jpeg"

            request, response = client.get("/fry/test.png")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/png"

            request, response = client.get("/fry/test.jpg")
            expect(response.status) == 200
            expect(response.headers["content-type"]) == "image/jpeg"
