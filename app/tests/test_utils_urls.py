import pytest

from .. import utils

URL_CLEANED = [
    # Trailing blank lines are dropped
    (
        "http://localhost:5000/images/iw/_.png",
        "http://localhost:5000/images/iw.png",
    ),
    (
        "http://localhost:5000/images/iw/a/_/_.png",
        "http://localhost:5000/images/iw/a.png",
    ),
    (
        "http://localhost:5000/images/iw/a/_.png?width=100",
        "http://localhost:5000/images/iw/a.png?width=100",
    ),
    # A blank line followed by more text is preserved
    (
        "http://localhost:5000/images/vince/a/_.b/c_d.png",
        "http://localhost:5000/images/vince/a/_.b/c_d.png",
    ),
    (
        "http://localhost:5000/images/vince/a/_.b/c-d.png",
        "http://localhost:5000/images/vince/a/_.b/c-d.png",
    ),
]


@pytest.mark.parametrize(("url", "cleaned"), URL_CLEANED)
def test_clean(expect, url, cleaned):
    expect(utils.urls.clean(url)) == cleaned
