# pylint: disable=unused-variable,misplaced-comparison-constant

import os

from .conftest import load

TESTS = os.path.dirname(__file__)
ROOT = os.path.dirname(TESTS)
IMAGES = os.path.join(ROOT, "data", "images")
LATEST = os.path.join(IMAGES, "latest.jpg")


def describe_get():

    def describe_visible():

        def basic(client):
            path = os.path.join(IMAGES, 'iw', 'hello', 'world.jpg')
            if os.path.exists(path):
                os.remove(path)

            response = client.get("/iw/hello/world.jpg")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype
            assert os.path.isfile(path)

        def with_only_1_line(client):
            response = client.get("/iw/hello.jpg")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype

        def with_lots_of_text(client):
            top = "-".join(["hello"] * 20)
            bottom = "-".join(["world"] * 20)
            response = client.get("/iw/" + top + "/" + bottom + ".jpg")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype

    def describe_hidden():

        def when_jpg(client):
            response = client.get("/_aXcJaGVsbG8vd29ybGQJ.jpg")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype

    def describe_alt():

        def when_valid(client):
            response = client.get("/sad-biden/hello.jpg?alt=scowl")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype

        def it_redirects_to_lose_alt_when_default(client):
            response = client.get("/sad-biden/hello.jpg?alt=default")

            assert 302 == response.status_code
            assert '<a href="/sad-biden/hello.jpg">' in \
                load(response, as_json=False)

        def it_redirects_to_lose_alt_when_unknown(client):
            response = client.get("/sad-biden/hello.jpg?alt=__unknown__")

            assert 302 == response.status_code
            assert '<a href="/sad-biden/hello.jpg">' in \
                load(response, as_json=False)

        def it_keeps_alt_after_template_redirect(client):
            response = client.get("/sad-joe/hello.jpg?alt=scowl")

            assert 302 == response.status_code
            assert '<a href="/sad-biden/hello.jpg?alt=scowl">' in \
                load(response, as_json=False)

        def it_keeps_alt_after_text_redirect(client):
            response = client.get("/sad-biden.jpg?alt=scowl")

            assert 302 == response.status_code
            assert '-vote.jpg?alt=scowl">' in \
                load(response, as_json=False)

    def describe_latest():

        def when_existing(client):
            open(LATEST, 'w').close()  # force the file to exist
            response = client.get("/latest.jpg")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype

        def when_missing(client):
            try:
                os.remove(LATEST)
            except FileNotFoundError:
                pass

            response = client.get("/latest.jpg")

            assert 200 == response.status_code
            assert 'image/png' == response.mimetype

    def describe_redirects():

        def when_missing_dashes(client):
            response = client.get("/iw/HelloThere_World/How-areYOU.jpg")

            assert 302 == response.status_code
            assert '<a href="/iw/hello-there-world/how-are-you.jpg">' in \
                load(response, as_json=False)

        def when_no_text(client):
            response = client.get("/live.jpg")

            assert 302 == response.status_code
            assert '<a href="/live/_/do-it-live!.jpg">' in \
                load(response, as_json=False)

        def when_aliased_template(client):
            response = client.get("/insanity-wolf/hello/world.jpg")

            assert 302 == response.status_code
            assert '<a href="/iw/hello/world.jpg">' in \
                load(response, as_json=False)

        def when_jpeg_extension_without_text(client):
            response = client.get("/iw.jpeg")

            assert 302 == response.status_code
            assert '<a href="/iw.jpg">' in \
                load(response, as_json=False)

        def when_jpeg_extension_with_text(client):
            response = client.get("/iw/hello/world.jpeg")

            assert 302 == response.status_code
            assert '<a href="/iw/hello/world.jpg">' in \
                load(response, as_json=False)

    def describe_errors():

        def when_unknown_template(client):
            response = client.get("/make/sudo/give.me.jpg")

            assert 200 == response.status_code
            assert 'image/jpeg' == response.mimetype
            # unit tests ensure this is a placeholder image

        def when_too_much_text_for_a_filename(client):
            top = "hello"
            bottom = "-".join(["world"] * 50)
            response = client.get("/iw/" + top + "/" + bottom + ".jpg")

            assert 414 == response.status_code
            assert {
                'message': "Filename too long."
            } == load(response)
