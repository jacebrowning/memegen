from backend.main import app
from pkg_resources import get_distribution


def describe_spec():
    def it_contains_the_version(expect):
        request, response = app.test_client.get("/swagger/swagger.json")
        expect(response.status) == 200
        expect(response.json["info"]["version"]) == get_distribution("memegen").version
