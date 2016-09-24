# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .conftest import load


def describe_get():

    def it_returns_link_options(client):
        response = client.get("/api/templates/iw/hello/world")

        expect(response.status_code) == 200
        assert dict(
            direct=dict(
                visible="http://localhost/iw/hello/world.jpg",
                masked="http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg",
            ),
            markdown=dict(
                visible="![iw](http://localhost/iw/hello/world.jpg)",
                masked="![iw](http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg)",
            ),
        ) == load(response)

    def with_top_only(client):
        response = client.get("/api/templates/iw/hello")

        expect(response.status_code) == 200
        assert dict(
            visible="http://localhost/iw/hello.jpg",
            masked="http://localhost/_aXcJaGVsbG8J.jpg",
        ) == load(response, key='direct')

    def with_bottom_only(client):
        response = client.get("/api/templates/iw/_/hello")

        expect(response.status_code) == 200
        assert dict(
            visible="http://localhost/iw/_/hello.jpg",
            masked="http://localhost/_aXcJXy9oZWxsbwkJ.jpg",
        ) == load(response, key='direct')

    def with_dashes(client):
        response = client.get("/api/templates/iw/HelloThere_World/How-areYOU")

        expect(response.status_code) == 302
        assert '<a href="/api/templates/iw/hello-there-world/how-are-you">' in \
            load(response, as_json=False)

    def when_masked(client):
        response = client.get("/_aXcJaGVsbG8vd29ybGQJ")

        expect(response.status_code) == 302
        assert '<a href="/api/templates/iw/hello/world">' in \
            load(response, as_json=False)

    def when_masked_with_1_line(client):
        response = client.get("/_aXcJaGVsbG8J")

        expect(response.status_code) == 302
        assert '<a href="/api/templates/iw/hello">' in \
            load(response, as_json=False)

    def when_alias(client):
        response = client.get("/api/templates/insanity-wolf")

        expect(response.status_code) == 302
        assert '<a href="/api/templates/iw">' in load(response, as_json=False)

    def when_alias_with_text(client):
        response = client.get("/api/templates/insanity-wolf/hello/world")

        expect(response.status_code) == 302
        assert '<a href="/api/templates/iw/hello/world">' in \
            load(response, as_json=False)

    def old_api_is_still_supported_via_redirect(client):
        response = client.get("/iw/top/bottom")

        assert 302 == response.status_code
        assert '<a href="/api/templates/iw/top/bottom">' in \
            load(response, as_json=False)
