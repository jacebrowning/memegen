# pylint: disable=unused-variable,misplaced-comparison-constant,expression-not-assigned

from expecter import expect

from .utils import load


def describe_get():

    def it_returns_link_options(client):
        status, data = load(client.get("/api/templates/iw/hello/world"))

        expect(status) == 200
        expect(data) == dict(
            direct=dict(
                visible="http://localhost/iw/hello/world.jpg",
                masked="http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg",
            ),
            markdown=dict(
                visible="![iw](http://localhost/iw/hello/world.jpg)",
                masked="![iw](http://localhost/_aXcJaGVsbG8vd29ybGQJ.jpg)",
            ),
        )

    def with_top_only(client):
        status, data = load(client.get("/api/templates/iw/hello"))

        expect(status) == 200
        expect(data['direct']) == dict(
            visible="http://localhost/iw/hello.jpg",
            masked="http://localhost/_aXcJaGVsbG8J.jpg",
        )

    def with_bottom_only(client):
        status, data = load(client.get("/api/templates/iw/_/hello"))

        expect(status) == 200
        expect(data['direct']) == dict(
            visible="http://localhost/iw/_/hello.jpg",
            masked="http://localhost/_aXcJXy9oZWxsbwkJ.jpg",
        )

    def with_dashes(client):
        status, data = load(client.get(
            "/api/templates/iw/HelloThere_World/How-areYOU"))

        expect(status) == 302
        expect(data).contains(
            '<a href="/api/templates/iw/hello_there_world/how_are_you">')

    def when_masked(client):
        status, data = load(client.get("/_aXcJaGVsbG8vd29ybGQJ"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/iw/hello/world">')

    def when_masked_with_1_line(client):
        status, data = load(client.get("/_aXcJaGVsbG8J"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/iw/hello">')

    def when_alias(client):
        status, data = load(client.get("/api/templates/insanity-wolf"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/iw">')

    def when_alias_with_text(client):
        status, data = load(client.get(
            "/api/templates/insanity-wolf/hello/world"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/iw/hello/world">')

    def old_api_is_still_supported_via_redirect(client):
        status, data = load(client.get("/iw/top/bottom"))

        expect(status) == 302
        expect(data).contains('<a href="/api/templates/iw/top/bottom">')
