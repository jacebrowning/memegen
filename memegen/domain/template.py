import os
import logging

import time
import requests
from PIL import Image

from .text import Text


log = logging.getLogger(__name__)


class Template:
    """Blank image to generate a meme."""

    DEFAULT = 'default'
    EXTENSIONS = ('.png', '.jpg')

    SAMPLE_LINES = ["YOUR TEXT", "GOES HERE"]

    VALID_LINK_FLAG = '.valid_link.tmp'

    MIN_HEIGHT = 240
    MIN_WIDTH = 240

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
        return self.key != other.key

    def __lt__(self, other):
        return self.name < other.name

    @property
    def path(self):
        return self.get_path()

    @property
    def default_text(self):
        return Text(self.lines)

    @property
    def default_path(self):
        return self.default_text.path or Text.EMPTY

    @property
    def sample_text(self):
        return self.default_text or Text(self.SAMPLE_LINES)

    @property
    def sample_path(self):
        return self.sample_text.path

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

    def get_path(self, *styles):
        for name in (n.lower() for n in (*styles, self.DEFAULT) if n):
            for extension in self.EXTENSIONS:
                path = os.path.join(self.root, self.key, name + extension)
                if os.path.isfile(path):
                    return path
        return None

    def validate(self, validators=None):
        if validators is None:
            validators = [
                self.validate_meta,
                self.validate_link,
                self.validate_size,
            ]
        for validator in validators:
            if not validator():
                return False
        return True

    def validate_meta(self):
        if not self.lines:
            log.error("Template '%s' has no default lines of text", self)
            return False
        if not self.name:
            log.error("Template '%s' has no name", self)
            return False
        if not self.name[0].isalnum():
            msg = "Template '%s' name %r should start with an alphanumeric"
            log.error(msg, self, self.name)
            return False
        if not self.path:
            log.error("Template '%s' has no default image", self)
            return False
        return True

    def validate_link(self):
        if self.link:
            flag = os.path.join(self.root, self.key, self.VALID_LINK_FLAG)
            if os.path.isfile(flag):
                log.info("Link already checked: %s", self.link)
            else:
                log.info("Checking link %s ...", self.link)
                try:
                    response = requests.get(self.link, timeout=5)
                except requests.exceptions.ReadTimeout:
                    log.warning("Connection timed out")
                    return True  # assume URL is OK; it will be checked again
                if response.status_code >= 400 and response.status_code != 429:
                    msg = "Template '%s' link is invalid (%s)"
                    log.error(msg, self, response.status_code)
                    return False
                else:
                    with open(flag, 'w') as stream:
                        stream.write(str(int(time.time())))
        return True

    def validate_size(self):
        im = Image.open(self.path)
        w, h = im.size
        if w < self.MIN_WIDTH or h < self.MIN_HEIGHT:
            log.error("Image must be at least %ix%i (is %ix%i)",
                      self.MIN_WIDTH, self.MIN_HEIGHT, w, h)
            return False
        return True
