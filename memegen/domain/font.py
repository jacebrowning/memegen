import logging


log = logging.getLogger(__name__)


class Font:
    """Font file used to render text onto an image."""

    def __init__(self, path):
        self.path = path

    @property
    def name(self):
        return self.path.stem.lower().replace('_', '-')
