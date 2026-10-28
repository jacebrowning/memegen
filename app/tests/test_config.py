import logging
from pathlib import Path

from bugsnag.utils import FilterDict, SanitizingJSONEncoder

from .. import config

API_KEY = "abcdef123456"
ROOT = Path(config.__file__).parent


def describe_bugsnag(expect, client):
    def it_redacts_credentials_from_request_metadata():
        request, _response = client.get(
            f"/images/iw/a.png?api_key={API_KEY}",
            headers={"X-API-KEY": "secret-header-value"},
        )
        metadata = config.BugsnagErrorHandler._metadata(request)
        encoder = SanitizingJSONEncoder(
            logging.getLogger(), keyword_filters=config.BUGSNAG_FILTERS
        )
        payload = encoder.encode(FilterDict(metadata))

        expect(payload).excludes(API_KEY)
        expect(payload).excludes("secret-header-value")


def describe_logging(expect, client, caplog):
    def it_does_not_log_api_keys_from_urls():
        caplog.set_level(logging.INFO)
        client.get(f"/images/iw/a.png?api_key={API_KEY}")
        messages = "\n".join(
            record.getMessage()
            for record in caplog.records
            if Path(record.pathname).is_relative_to(ROOT)
        )
        expect(messages).contains("Rendering image")
        expect(messages).excludes(API_KEY)
