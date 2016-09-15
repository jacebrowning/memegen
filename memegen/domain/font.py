from pathlib import Path
import logging


log = logging.getLogger(__name__)


class Font:
    """Font file used to render text onto an image."""

    def __init__(self, path):
        self._path = path

    def __str__(self):
        return self.path

    @property
    def name(self):
        return self._path.stem.lower().replace('_', '-')

    @property
    def path(self):
        return str(self._path)

    @path.setter
    def path(self, value):
        self._path = Path(value)
