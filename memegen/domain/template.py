import os
import hashlib
import shutil
from pathlib import Path
import tempfile
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

    def __init__(self, key, name=None, lines=None, aliases=None, link=None,
                 root=None):
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
    def dirpath(self):
        return os.path.join(self.root, self.key)

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

    @property
    def styles(self):
        return sorted(self._styles())

    def _styles(self):
        """Yield all template style names."""
        for filename in os.listdir(self.dirpath):
            name, ext = os.path.splitext(filename.lower())
            if ext in self.EXTENSIONS and name != self.DEFAULT:
                yield name

    @property
    def keywords(self):
        words = set()
        for fields in [self.key, self.name] + self.aliases + self.lines:
            for word in fields.lower().replace(Text.SPACE, ' ').split(' '):
                if word:
                    words.add(word)
        return words

    @staticmethod
    def strip(text, keep_special=False):
        text = text.lower().strip().replace(' ', '-')
        if not keep_special:
            for char in ('-', '_', '!', "'"):
                text = text.replace(char, '')
        return text

    def get_path(self, *styles):
        for style in styles:
            path = download_image(style)
            if path:
                return path

        for name in (n.lower() for n in (*styles, self.DEFAULT) if n):
            for extension in self.EXTENSIONS:
                path = Path(self.dirpath, name + extension)
                try:
                    if path.is_file():
                        return path
                except OSError:
                    continue

        return None

    def search(self, query):
        """Count the number of times a query exists in relevant fields."""
        if query is None:
            return -1

        count = 0

        for field in [self.key, self.name] + self.aliases + self.lines:
            count += field.lower().count(query.lower())

        return count

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
            self._error("has no default lines of text")
            return False
        if not self.name:
            self._error("has no name")
            return False
        if not self.name[0].isalnum():
            self._error("name %r should start with an alphanumeric", self.name)
            return False
        if not self.path:
            self._error("has no default image")
            return False
        return True

    def validate_link(self):
        if self.link:
            flag = Path(self.dirpath, self.VALID_LINK_FLAG)
            if flag.is_file():
                log.info("Link already checked: %s", self.link)
            else:
                log.info("Checking link %s ...", self.link)
                try:
                    response = requests.head(self.link, timeout=5)
                except requests.exceptions.ReadTimeout:
                    log.warning("Connection timed out")
                    return True  # assume URL is OK; it will be checked again
                if response.status_code in [403, 429]:
                    self._warn("link is unavailable (%s)", response.status_code)
                elif response.status_code >= 400:
                    self._error("link is invalid (%s)", response.status_code)
                    return False
                else:
                    with open(str(flag), 'w') as stream:
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

    def _warn(self, fmt, *objects):
        log.warning("Template '%s' " + fmt, self, *objects)

    def _error(self, fmt, *objects):
        log.error("Template '%s' " + fmt, self, *objects)


class Placeholder:
    """Default image for missing templates."""

    path = None

    def __init__(self, key):
        self.key = key

    @staticmethod
    def get_path(*styles):
        path = None

        for style in styles:
            path = download_image(style)
            if path:
                break

        if not path:
            path = os.path.dirname(__file__) + "/../static/images/missing.png"

        return path


def download_image(url):
    if not url or not url.startswith("http"):
        return None

    path = Path(tempfile.gettempdir(),
                hashlib.md5(url.encode('utf-8')).hexdigest())

    if path.is_file():
        log.debug("Already downloaded: %s", url)
        return path

    try:
        response = requests.get(url, stream=True)
    except requests.exceptions.InvalidURL:
        log.error("Invalid link: %s", url)
        return None
    except requests.exceptions.ConnectionError:
        log.error("Bad connection: %s", url)
        return None

    if response.status_code == 200:
        log.info("Downloading %s", url)
        with open(str(path), 'wb') as outfile:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, outfile)
        return path

    log.error("Unable to download: %s", url)
    return None
