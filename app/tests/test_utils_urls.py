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


URL_REDACTED = [
    (
        "http://localhost:5000/images/iw/a.png?api_key=abcdef123456",
        "http://localhost:5000/images/iw/a.png?api_key=ab***56",
    ),
    (
        "http://localhost:5000/images/iw/a.png?width=100&token=xyz789xyz&height=50",
        "http://localhost:5000/images/iw/a.png?width=100&token=xy***yz&height=50",
    ),
    (
        "http://localhost:5000/images/iw/a.png?token=abc",
        "http://localhost:5000/images/iw/a.png?token=***",
    ),
    (
        "http://localhost:5000/images/iw/a.png?background=http://x.com/token=1.png",
        "http://localhost:5000/images/iw/a.png?background=http://x.com/token=1.png",
    ),
]


@pytest.mark.parametrize(("url", "redacted"), URL_REDACTED)
def test_redact(expect, url, redacted):
    expect(utils.urls.redact(url)) == redacted
