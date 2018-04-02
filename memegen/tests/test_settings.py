# pylint: disable=unused-variable,expression-not-assigned

from memegen.settings import get_config


def describe_get_config():

    def when_valid(expect):
        config = get_config('production')
        expect(config.ENV) == 'production'

    def when_extended(expect):
        config = get_config('staging')
        expect(config.ENV) == 'staging'

    def when_empty(expect):
        with expect.raises(AssertionError):
            get_config('')

    def when_unknown(expect):
        with expect.raises(AssertionError):
            get_config('unknown')
