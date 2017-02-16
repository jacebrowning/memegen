"""Tests for template pattern matching."""
# pylint: disable=expression-not-assigned

import pytest
from expecter import expect

from .utils import load


BASE = "http://localhost/api/templates/"


@pytest.mark.parametrize("pattern,links", [

    ("take my money", [
        BASE + "money/_/take-my-money",
    ]),

    ("shut up and take my money", [
        BASE + "money/shut-up-and/take-my-money",
    ]),

    ("shut up and do that thing", [
        BASE + "money/shut-up-and/do-that-thing",
    ]),

    ("stop talking and take my money", [
        BASE + "money/stop-talking-and/take-my-money",
    ]),

    ("oops i should not have said that", [
        BASE + "hagrid/oops/i-should-not-have-said-that",
    ]),

    ("we should not have done that", [
        BASE + "hagrid/_/we-should-not-have-done-that",
    ]),

    ("they shouldn't have done that", [
        BASE + "hagrid/_/they-shouldn't-have-done-that",
    ]),

    ("we found something so we got that, which is nice", [
        BASE + "nice/we-found-something/so-we-got-that,-which-is-nice",
    ]),

    ("'member star wars", [
        BASE + "mb/'member/star-wars",
    ]),

    ("remember the good times", [
        BASE + "mb/member/the-good-times",
    ]),

])
def test_match(client, pattern, links):
    response = client.get("/api/magic/" + pattern, follow_redirects=True)

    _, matches = load(response)

    expect([match['link'] for match in matches]) == links
