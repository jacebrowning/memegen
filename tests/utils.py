import json
import logging
from typing import Union

import flask


log = logging.getLogger(__name__)


def load(response: flask.Response) -> (int, Union[dict, str]):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')

    if text:
        try:
            data = json.loads(text)
        except json.decoder.JSONDecodeError:
            data = text
    else:
        data = None

    log.debug("Response: %r", data)

    return response.status_code, data
