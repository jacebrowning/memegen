# pylint: disable=unused-variable,unused-argument,misplaced-comparison-constant,expression-not-assigned,singleton-comparison

import os

import pytest
from expecter import expect

from memegen.routes.image import cache_filtered, cache_unfiltered

from .utils import load

TESTS = os.path.dirname(__file__)
ROOT = os.path.dirname(TESTS)
IMAGES = os.path.join(ROOT, 'data', 'images')


def describe_get():

    def describe_visible():

        def with_nominal_text(client):
            path = os.path.join(IMAGES, 'iw', 'hello', 'world' + '.img')
            if os.path.exists(path):
                os.remove(path)

            response = client.get("/iw/hello/world.jpg?watermark=none")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'
            expect(os.path.isfile(path)) == True

        def with_only_1_line(client):
            response = client.get("/iw/hello.jpg")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        @pytest.mark.xfail(os.name == 'nt', reason="Windows has a path limit")
        def with_lots_of_text(client):
            top = "_".join(["hello"] * 20)
            bottom = "_".join(["world"] * 20)
            response = client.get("/iw/" + top + "/" + bottom + ".jpg")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

    def describe_hidden():

        def when_jpg(client):
            response = client.get("/_aXcJaGVsbG8vd29ybGQJ.jpg")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

    def describe_custom_style():

        def when_provided(client):
            response = client.get("/sad-biden/hello.jpg?alt=scowl")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        def it_redirects_to_lose_alt_when_default_style(client):
            status, data = load(client.get("/sad-biden/hello.jpg?alt=default"))

            expect(status) == 302
            expect(data).contains('<a href="/sad-biden/hello.jpg">')

        def it_redirects_to_lose_alt_when_unknown_style(client):
            status, data = load(client.get(
                "/sad-biden/hello.jpg?alt=__unknown__"))

            expect(status) == 302
            expect(data).contains('<a href="/sad-biden/hello.jpg">')

        def it_keeps_alt_after_template_redirect(client):
            status, data = load(client.get("/sad-joe/hello.jpg?alt=scowl"))

            expect(status) == 302
            expect(data).contains('<a href="/sad-biden/hello.jpg?alt=scowl">')

        def it_keeps_alt_after_text_redirect(client):
            status, data = load(client.get("/sad-biden.jpg?alt=scowl"))

            expect(status) == 302
            expect(data).contains("_vote.jpg")
            expect(data).contains("alt=scowl")

        def when_url(client):
            url = "http://www.gstatic.com/webp/gallery/1.jpg"
            response = client.get("/sad-biden/hello.jpg?alt=" + url)

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        def it_returns_an_error_with_non_image_urls(client):
            url = "http://example.com"
            response = client.get("/sad-biden/hello.jpg?alt=" + url)

            expect(response.status_code) == 415

        def it_handles_png_int32_pixels(client):
            url = "https://raw.githubusercontent.com/jacebrowning/memegen/master/tests/files/201692816359570.jpeg"
            response = client.get("/sad-biden/hello.jpg?alt=" + url)

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        def it_handles_jpg_cmyk_pixels(client):
            url = "https://raw.githubusercontent.com/jacebrowning/memegen/master/tests/files/Channel_digital_image_CMYK_color.jpg"
            response = client.get("/sad-biden/hello.jpg?alt=" + url)

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        def it_redirects_to_lose_alt_when_unknown_url(client):
            url = "http://example.com/not/a/real/image.jpg"
            status, data = load(client.get("/sad-biden/hello.jpg?alt=" + url))

            expect(status) == 302
            expect(data).contains(
                '<a href="/sad-biden/hello.jpg">')

        def it_redirects_to_lose_alt_when_bad_url(client):
            url = "http:invalid"
            status, data = load(client.get("/sad-biden/hello.jpg?alt=" + url))

            expect(status) == 302
            expect(data).contains('<a href="/sad-biden/hello.jpg">')

    def describe_custom_font():

        def when_provided(client):
            response = client.get("/iw/hello.jpg?font=impact")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        def it_redirects_on_unknown_fonts(client):
            status, data = load(client.get("/iw/hello.jpg?font=__unknown__"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/hello.jpg">')

        def it_keeps_font_after_redirect(client):
            status, data = load(client.get("/iw/what%3F.jpg?font=impact"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/what~q.jpg?font=impact">')

    def describe_custom_size():

        def it_keeps_size_after_redirect(client):
            status, data = load(client.get(
                "/iw/what%3F.jpg?width=67&height=89"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/what~q.jpg?')
            expect(data).contains('width=67')
            expect(data).contains('height=89')

    def describe_watermark():

        def it_accept_supported_watermark(client):
            response = client.get("/iw/test.jpg?watermark=test")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'

        def it_redirects_with_unsupported_watermark(client):
            status, data = load(client.get(
                "/iw/test.jpg?watermark=unsupported"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/test.jpg"')

        def it_keeps_watermark_after_redirect(client):
            status, data = load(client.get("/iw/test 2.jpg?watermark=test"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/test_2.jpg?watermark=test"')

    def describe_preview():

        def it_keeps_flag_after_redirect(client):
            status, data = load(client.get(
                "/iw/i am still typi.jpg?preview=true"))

            expect(status) == 302
            expect(data).contains(
                '<a href="/iw/i_am_still_typi.jpg?preview=true">')

    def describe_latest():

        @pytest.fixture()
        def enable_cache():
            cache_filtered.disabled = False
            cache_unfiltered.disabled = False
            cache_filtered.items = []
            cache_unfiltered.items = []

        @pytest.fixture()
        def disable_cache():
            cache_filtered.disabled = True
            cache_unfiltered.disabled = True
            cache_filtered.items = []
            cache_unfiltered.items = []

        def it_returns_the_last_image(client, enable_cache):
            client.get("/iw/my_first_meme.jpg")

            status, data = load(client.get("/latest.jpg"))

            expect(status) == 302
            expect(data).contains(
                '<a href="http://localhost/iw/my_first_meme.jpg?preview=true">')

        def it_returns_a_placeholder_with_an_empty_cache(client, disable_cache):
            status, data = load(client.get("/latest.jpg"))

            expect(status) == 302
            expect(data).contains(
                '<a href="http://localhost/custom/your_meme/goes_here.jpg'
                '?alt=https://raw.githubusercontent.com/jacebrowning/memegen/'
                'master/memegen/static/images/missing.png">')

        def it_filters_blocked_words(client, enable_cache):
            client.get("/iw/nazis.jpg")

            status, data = load(client.get("/latest.jpg"))

            expect(status) == 302
            expect(data).excludes(
                '<a href="http://localhost/iw/nazis.jpg')

            status, data = load(client.get("/latest.jpg?filtered=false"))

            expect(status) == 302
            expect(data).contains(
                '<a href="http://localhost/iw/nazis.jpg?preview=true">')

        def it_filters_custom_images(client, enable_cache):
            client.get("/custom/test.jpg")

            status, data = load(client.get("/latest.jpg"))

            expect(status) == 302
            expect(data).excludes(
                '<a href="http://localhost/custom/test.jpg')

            status, data = load(client.get("/latest.jpg?filtered=false"))

            expect(status) == 302
            expect(data).contains(
                '<a href="http://localhost/custom/test.jpg?preview=true">')

    def describe_redirects():

        def when_missing_dashes(client):
            status, data = load(client.get(
                "/iw/HelloThere_World/How-areYOU.jpg"))

            expect(status) == 302
            expect(data).contains(
                '<a href="/iw/hello_there_world/how_are_you.jpg">')

        def when_no_text(client):
            status, data = load(client.get("/live.jpg"))

            expect(status) == 302
            expect(data).contains('<a href="/live/_/do_it_live!.jpg">')

        def when_aliased_template(client):
            status, data = load(client.get("/insanity-wolf/hello/world.jpg"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/hello/world.jpg">')

        def when_jpeg_extension_without_text(client):
            status, data = load(client.get("/iw.jpeg"))

            expect(status) == 302
            expect(data).contains('<a href="/iw.jpg">')

        def when_jpeg_extension_with_text(client):
            status, data = load(client.get("/iw/hello/world.jpeg"))

            expect(status) == 302
            expect(data).contains('<a href="/iw/hello/world.jpg">')

    def describe_errors():

        def when_unknown_template(client):
            response = client.get("/make/sudo/give.me.jpg")

            expect(response.status_code) == 200
            expect(response.mimetype) == 'image/jpeg'
            # unit tests ensure this is a placeholder image

        @pytest.mark.xfail(os.name == 'nt', reason="Windows has a path limit")
        def when_too_much_text_for_a_filename(client):
            top = "hello"
            bottom = "_".join(["world"] * 50)
            url = "/iw/" + top + "/" + bottom + ".jpg"
            status, data = load(client.get(url))

            expect(status) == 414
            expect(data) == {
                'message': "Filename too long."
            }
