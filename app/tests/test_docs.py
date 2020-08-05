from pkg_resources import get_distribution


def describe_spec():
    def it_contains_the_version(expect, client):
        request, response = client.get("/api/docs/swagger.json")
        expect(response.status) == 200
        expect(response.json["info"]["version"]) == get_distribution("memegen").version
