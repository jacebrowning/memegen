"""Tests for template pattern matching."""
# pylint: disable=expression-not-assigned

import pytest
from expecter import expect

from .utils import load


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

    ("oops i should not have said that", [
        "http://localhost/hagrid/oops/i-should-not-have-said-that",
    ]),

    ("we should not have done that", [
        "http://localhost/hagrid/_/we-should-not-have-done-that",
    ]),

    ("they shouldn't have done that", [
        "http://localhost/hagrid/_/they-shouldn't-have-done-that",
    ]),

])
def test_match(client, pattern, links):
    response = client.get("/magic/" + pattern, follow_redirects=True)

    _, matches = load(response)

    expect([match['link'] for match in matches]) == links
