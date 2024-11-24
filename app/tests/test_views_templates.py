import json

import pytest


def describe_list():
    def describe_GET():
        @pytest.mark.slow
        @pytest.mark.parametrize("slash", ["", "/"])
        def it_returns_all_templates(expect, client, slash):
            request, response = client.get("/templates" + slash, timeout=15)
            expect(response.status) == 200
            expect(len(response.json)) >= 140

        @pytest.mark.slow
        def it_can_filter_templates(expect, client):
            request, response = client.get("/templates?filter=awesome", timeout=15)
            expect(response.status) == 200
            expect(len(response.json)) == 3


def describe_detail():
    def describe_GET():
        @pytest.mark.parametrize("slash", ["", "/"])
        def it_includes_metadata(expect, client, slash):
            request, response = client.get("/templates/iw" + slash)
            expect(response.status) == 200
            expect(response.json) == {
                "id": "iw",
                "name": "Insanity Wolf",
                "lines": 2,
                "overlays": 1,
                "styles": ["default"],
                "blank": "http://localhost:5000/images/iw.png",
                "example": {
                    "text": ["does testing", "in production"],
                    "url": "http://localhost:5000/images/iw/does_testing/in_production.png",
                },
                "source": "http://knowyourmeme.com/memes/insanity-wolf",
                "keywords": [],
                "_self": "http://localhost:5000/templates/iw",
            }

        def it_defaults_to_webp_example_when_available(expect, client):
            request, response = client.get("/templates/bongo")
            expect(response.status) == 200
            expect(response.json["example"]["url"]) == (
                "http://localhost:5000/images/bongo/"
                "Any_sound_when_you're_trying_to_sleep/Max_volume_alarm_when_you_have_to_wake_up.webp"
            )

        def it_returns_404_when_missing(expect, client):
            request, response = client.get("/templates/foobar")
            expect(response.status) == 404

    def describe_POST():
        @pytest.mark.parametrize("as_json", [True, False])
        def it_returns_an_image_url(expect, client, as_json):
            data = {"text_lines[]": ["foo", "bar"], "extension": "jpg"}
            kwargs: dict = {"content": json.dumps(data)} if as_json else {"data": data}
            request, response = client.post("/templates/iw", **kwargs)

            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.jpg"
            }

        @pytest.mark.parametrize("as_json", [True, False])
        def it_supports_custom_backgrounds(expect, client, as_json):
            data = {
                "background": "https://www.gstatic.com/webp/gallery/3.png",
                "text_lines[]": ["foo", "bar"],
                "extension": "jpg",
            }
            kwargs: dict = {"content": json.dumps(data)} if as_json else {"data": data}
            request, response = client.post("/templates/custom", **kwargs)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.jpg"
                "?background=https://www.gstatic.com/webp/gallery/3.png"
            }

        def it_accepts_template_id_as_custom_background(expect, client):
            data = {
                "background": "fry",
                "text_lines[]": ["foo", "bar"],
                "extension": "jpg",
            }
            request, response = client.post("/templates/custom", data=data)
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/fry/foo/bar.jpg"
            }

        @pytest.mark.parametrize("id", ["iw", "custom"])
        def it_redirects_if_requested(expect, client, id):
            data = {"text_lines": ["abc"], "redirect": True}
            request, response = client.post(
                f"/templates/{id}", data=data, allow_redirects=False
            )
            redirect = f"http://localhost:5000/images/{id}/abc.png?status=201"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect

        def it_handles_unknown_template_id(expect, client, unknown_template):
            data = {"text_lines": ["one", "two"]}
            request, response = client.post(
                f"/templates/{unknown_template.id}", data=data
            )
            expect(response.status) == 404
            expect(response.json) == {
                "url": "http://localhost:5000/images/unknown/one/two.png"
            }
