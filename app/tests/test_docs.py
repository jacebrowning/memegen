from pkg_resources import get_distribution


def describe_spec():
    def it_contains_the_version(expect, client):
        version = get_distribution("memegen").version
        request, response = client.get("/docs/swagger.json")
        expect(response.status) == 200
        expect(response.json["info"]["version"]) == version

    def describe_image_list():
        def it_contains_the_operation_id(expect, client):
            request, response = client.get("/docs/swagger.json")
            operation = response.json["paths"]["/images"]["post"]["operationId"]
            expect(operation) == "Memes.create"

        def it_contains_the_request_spec(expect, client):
            request, response = client.get("/docs/swagger.json")
            request_spec = response.json["paths"]["/images"]["post"]
            expect(request_spec["consumes"]) == ["application/json"]
            expect(request_spec["parameters"][0]) == {
                "schema": {
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "string"},
                        "text_lines": {"type": "array", "items": {"type": "string"}},
                        "style": {"type": "array", "items": {"type": "string"}},
                        "extension": {"type": "string"},
                        "redirect": {"type": "boolean"},
                    },
                },
                "name": "body",
                "required": False,
                "in": "body",
            }

        def it_contains_the_response_spec(expect, client):
            request, response = client.get("/docs/swagger.json")
            response_spec = response.json["paths"]["/images"]["post"]["responses"]
            # Successful response
            expect(response_spec["201"]["description"]) == (
                "Successfully created a meme"
            )
            expect(response_spec["201"]["schema"]) == {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
            }
            # Error response
            expect(response_spec["400"]["description"]) == (
                'Required "template_id" missing in request body'
            )
            expect(response_spec["400"]["schema"]) == {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            }
