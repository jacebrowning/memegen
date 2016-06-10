from pathlib import Path

from ..domain import Font


class FontStore:

    def __init__(self, root):
        self._items = {}
        for path in Path(root).iterdir():
            font = Font(path)
            self._items[font.name] = font

    def all(self):
        return self._items

    def find(self, key):
        try:
            return self._items[key]
        except KeyError:
            return None
