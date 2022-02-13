from pkg_resources import get_distribution


def describe_spec():
    def it_contains_the_version(expect, client):
        version = get_distribution("memegen").version
        request, response = client.get("/docs/openapi.json")
        expect(response.status) == 200
        expect(response.json["info"]["version"]) == version
