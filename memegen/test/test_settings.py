import pytest

from memegen.settings import Config, get_config


class TestGetConfig:

    def test_get_valid(self):
        config = get_config('prod')
        assert issubclass(config, Config)

    def test_get_none(self):
        with pytest.raises(AssertionError):
            get_config('')

    def test_get_unknown(self):
        with pytest.raises(AssertionError):
            get_config('not_a_valid_config')
