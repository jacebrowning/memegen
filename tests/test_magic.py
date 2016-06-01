"""Tests for template pattern matching."""
# pylint: disable=expression-not-assigned

import pytest
from expecter import expect

from .conftest import load


@pytest.mark.parametrize("pattern,links", [

    ("take my money", [
        "http://localhost/money/_/take-my-money",
    ]),

    ("shut up and take my money", [
        "http://localhost/money/shut-up-and/take-my-money",
    ]),

    ("shut up and do that thing", [
        "http://localhost/money/shut-up-and/do-that-thing",
    ]),

    ("stop talking and take my money", [
        "http://localhost/money/stop-talking-and/take-my-money",
    ]),

])
def test_match(client, pattern, links):
    response = client.get("/magic/" + pattern, follow_redirects=True)

    matches = load(response)

    expect([match['link'] for match in matches]) == links
