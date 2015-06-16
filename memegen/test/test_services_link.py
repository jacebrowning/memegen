import pytest


class TestLinkService:

    def test_decode_encoded_parts(self, link_service):
        code = link_service.encode("a", "b", "c")
        parts = link_service.decode(code)
        assert ("a", "b", "c") == parts

    def test_decode_invalid_code(self, link_service):
        with pytest.raises(ValueError):
            link_service.decode("bad_code")

    def test_decode_empty_code(self, link_service):
        with pytest.raises(ValueError):
            link_service.decode(b"")
