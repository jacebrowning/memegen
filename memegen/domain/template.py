import os
import re
import hashlib
import shutil
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

    def __init__(self, key, name=None, lines=None, patterns=None,
                 aliases=None, link=None, root=None):
        self.key = key
        self.name = name or ""
        self.lines = lines or []
        self.regexes = []
        self.aliases = aliases or []
        self.link = link or ""
        self.root = root or ""
        self.compile_regexes(patterns or [])

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
                path = os.path.join(self.dirpath, name + extension)
                if os.path.isfile(path):
                    return path

        return None

    def compile_regexes(self, patterns):
        self.regexes = [re.compile(p, re.IGNORECASE) for p in patterns]

    def match(self, string):
        if self.regexes:
            log.debug("Matching patterns in %s", self)

        for regex in self.regexes:
            log.debug("Comparing %r to %r", string, regex.pattern)
            result = regex.match(string)
            if result:
                ratio = round(min(len(regex.pattern) / len(string),
                                  len(string) / len(regex.pattern)), 2)
                path = Text(result.group(1) + '/' + result.group(2)).path
                log.debug("Matched: %r", ratio)
                return ratio, path

        return 0, None

    def validate(self, validators=None):
        if validators is None:
            validators = [
                self.validate_meta,
                self.validate_link,
                self.validate_size,
                self.validate_regexes,
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
            flag = os.path.join(self.dirpath, self.VALID_LINK_FLAG)
            if os.path.isfile(flag):
                log.info("Link already checked: %s", self.link)
            else:
                log.info("Checking link %s ...", self.link)
                try:
                    response = requests.get(self.link, timeout=5)
                except requests.exceptions.ReadTimeout:
                    log.warning("Connection timed out")
                    return True  # assume URL is OK; it will be checked again
                if response.status_code in [403, 429]:
                    self._warn("link is unavailable (%s)", response.status_code)
                elif response.status_code >= 400:
                    self._error("link is invalid (%s)", response.status_code)
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

    def validate_regexes(self):
        if not self.regexes:
            self._warn("has no regexes")
        for regex in self.regexes:
            pattern = regex.pattern
            if ")/?(" not in pattern:
                self._error("regex missing separator: %r", pattern)
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

    # /tmp is detroyed after every Heroku request
    path = "/tmp/" + hashlib.md5(url.encode('utf-8')).hexdigest()
    if os.path.isfile(path):
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
        with open(path, 'wb') as outfile:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, outfile)
        return path

    log.error("Unable to download: %s", url)
    return None
