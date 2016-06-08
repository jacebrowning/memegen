
import json
import logging

log = logging.getLogger(__name__)


def load(response, as_json=True, key=None):
    """Convert a response's binary data (JSON) to a native data type.

    :param reponse: Flask `Response` object.
    :param bool as_json: Treat the response's data as JSON.
    :param str key: Dictionary key to return the value of, `None` for all.

    """
    text = response.data.decode('utf-8')

    if not as_json:
        return response.status_code, text
    if text:
        data = json.loads(text)
        if key:
            data = data[key]
    else:
        data = None

    log.debug("Response: %r", data)

    return response.status_code, data
