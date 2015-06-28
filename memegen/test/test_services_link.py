# pylint: disable=R,C

import pytest


class TestLinkService:

    def test_decode_encoded_parts(self, link_service):
        code = link_service.encode("key", "my/path")
        parts = link_service.decode(code)
        assert ("key", "my/path") == parts

    def test_decode_invalid_code(self, link_service):
        with pytest.raises(ValueError):
            link_service.decode("bad_code")

    def test_decode_empty_code(self, link_service):
        with pytest.raises(ValueError):
            link_service.decode(b"")
