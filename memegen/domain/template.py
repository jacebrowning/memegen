import os

from .text import Text


class Template:
    """Blank image to generate a meme."""

    DEFAULTS = ("default.png", "default.jpg")

    def __init__(self, key,
                 name=None, lines=None, aliases=None, link=None, root=None):
        self.key = key
        self.name = name or ""
        self.lines = lines or []
        self.aliases = aliases or []
        self.link = link or ""
        self.root = root

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.name < other.name

    @property
    def path(self):
        for default in self.DEFAULTS:
            path = os.path.join(self.root, self.key, default)
            if os.path.isfile(path):
                return path
        return None

    @property
    def default(self):
        text = Text('/'.join(self.lines))
        return text.path
