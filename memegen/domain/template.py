import os
import logging

import requests

from .text import Text


log = logging.getLogger(__name__)


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
        self.root = root or ""

    def __str__(self):
        return self.key

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

    @property
    def aliases_lowercase(self):
        return [self.strip(a, keep_special=True) for a in self.aliases]

    @property
    def aliases_stripped(self):
        return [self.strip(a, keep_special=False) for a in self.aliases]

    @staticmethod
    def strip(text, keep_special=False):
        text = text.lower().strip().replace(' ', '-')
        if not keep_special:
            for char in ('-', '_', '!', "'"):
                text = text.replace(char, '')
        return text

    def validate(self):
        if not self.name:
            log.error("template '%s' has no name", self)
            return False
        if not self.name[0].isalnum():
            msg = "template '%s' name %r should start with an alphanumeric"
            log.error(msg, self, self.name)
            return False
        if not self.path:
            log.error("template '%s' has no default image", self)
            return False
        if self.link:
            log.info("checking link %s ...", self.link)
            response = requests.get(self.link)
            if response.status_code >= 400:
                return False
        return True
