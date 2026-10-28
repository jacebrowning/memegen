from unittest.mock import Mock

import pytest

from .. import helpers, settings
from ..models import Template


def describe_get_base_templates():
    @pytest.fixture
    def loader(monkeypatch):
        monkeypatch.setattr(helpers, "_templates", [])
        mock = Mock(return_value=[Template.objects.get("fry")])
        monkeypatch.setattr(helpers, "_load_base_templates", mock)
        return mock

    def it_reloads_templates_locally(expect, loader, monkeypatch):
        monkeypatch.setattr(settings, "DEPLOYED", False)
        helpers.get_base_templates()
        helpers.get_base_templates()
        expect(loader.call_count) == 2

    def it_caches_templates_when_deployed(expect, loader, monkeypatch):
        monkeypatch.setattr(settings, "DEPLOYED", True)
        first = helpers.get_base_templates()
        second = helpers.get_base_templates()
        expect(loader.call_count) == 1
        expect(second) == first

    def it_returns_a_copy_of_the_cache(expect, loader, monkeypatch):
        monkeypatch.setattr(settings, "DEPLOYED", True)
        helpers.get_base_templates().clear()
        expect(len(helpers.get_base_templates())) == 1
        expect(loader.call_count) == 1


def describe_get_valid_templates():
    @pytest.mark.slow
    def it_reuses_cached_templates_when_deployed(expect, client, monkeypatch):
        monkeypatch.setattr(settings, "DEPLOYED", True)
        monkeypatch.setattr(helpers, "_templates", [])

        request, response = client.get("/templates", timeout=15)
        expect(response.status) == 200
        expect(len(response.json)) >= 140
        expect(len(helpers._templates)) == len(response.json)

        monkeypatch.setattr(helpers, "_load_base_templates", Mock(return_value=[]))
        request, response2 = client.get("/templates", timeout=15)
        expect(response2.json) == response.json

        request, response = client.get("/templates?filter=awesome", timeout=15)
        expect(len(response.json)) == 3
