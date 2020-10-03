from pkg_resources import get_distribution


def describe_spec():
    def it_contains_the_version(expect, client):
        version = get_distribution("memegen-api").version
        request, response = client.get("/docs/swagger.json")
        expect(response.status) == 200
        expect(response.json["info"]["version"]) == version

    def describe_image_list():
        # Only spot checking the POST /images route, not sure
        # how valuable it would be to check the rest exhaustively?
        def it_contains_the_operation_id(expect, client):
            request, response = client.get("/docs/swagger.json")
            # This is our custom operationId, the default was images.index
            expect(response.json["paths"]["/images"]["post"]["operationId"]) == "images.create"

        def it_contains_the_request_spec(expect, client):
            request, response = client.get("/docs/swagger.json")
            request_spec = response.json["paths"]["/images"]["post"]
            expect(request_spec["consumes"]) == ["application/json"]
            expect(request_spec["parameters"][0]) == {
                "schema": {
                    "type": "object",
                    "properties": {
                        "template_key": {
                            "type": "string"
                        },
                        "text_lines": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "extension": {
                            "type": "string"
                        },
                        "redirect": {
                            "type": "boolean"
                        }
                    }
                },
                "name": "body",
                "required": False,
                "in": "body"
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
                    "url": {
                        "type": "string"
                    },
                }
            }
            # Error response
            expect(response_spec["400"]["description"]) == (
                'Required "template_key" missing in request body'
            )
            expect(response_spec["400"]["schema"]) == {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string"
                    },
                }
            }
