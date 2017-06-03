"""Tests for template pattern matching."""
# pylint: disable=expression-not-assigned

import pytest
from expecter import expect

from .utils import load


BASE = "http://localhost/api/templates/"


@pytest.mark.parametrize("pattern,links", [

    ("take my money", [
        BASE + "money/_/take_my_money",
    ]),

    ("shut up and take my money", [
        BASE + "money/shut_up_and/take_my_money",
    ]),

    ("shut up and do that thing", [
        BASE + "money/shut_up_and/do_that_thing",
    ]),

    ("stop talking and take my money", [
        BASE + "money/stop_talking_and/take_my_money",
    ]),

    ("oops i should not have said that", [
        BASE + "hagrid/oops/i_should_not_have_said_that",
    ]),

    ("we should not have done that", [
        BASE + "hagrid/_/we_should_not_have_done_that",
    ]),

    ("they shouldn't have done that", [
        BASE + "hagrid/_/they_shouldn't_have_done_that",
    ]),

    ("we found something so we got that, which is nice", [
        BASE + "nice/we_found_something/so_we_got_that,_which_is_nice",
    ]),

    ("'member star wars", [
        BASE + "mb/'member/star_wars",
    ]),

    ("remember the good times", [
        BASE + "mb/member/the_good_times",
    ]),

])
def test_match(client, pattern, links):
    response = client.get("/api/magic/" + pattern, follow_redirects=True)

    _, matches = load(response)

    expect([match['link'] for match in matches]) == links
