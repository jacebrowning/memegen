# pylint: disable=no-member

import os
import shutil
from contextlib import suppress
import logging

log = logging.getLogger(__name__)


class ImageStore:

    LATEST = "latest.jpg"

    def __init__(self, root, config):
        self.root = root
        self.regenerate_images = config.get('REGENERATE_IMAGES', False)

    @property
    def latest(self):
        return os.path.join(self.root, self.LATEST)

    def exists(self, image):
        image.root = self.root
        # TODO: add a way to determine if the styled image was already generated
        return os.path.isfile(image.path) and not image.style

    def create(self, image):
        if self.exists(image) and not self.regenerate_images:
            return

        image.root = self.root
        image.generate()

        with suppress(IOError):
            os.remove(self.latest)
        shutil.copy(image.path, self.latest)
