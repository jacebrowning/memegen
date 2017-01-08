import logging

import yorm
from yorm.types import List, Object
import profanityfilter


log = logging.getLogger(__name__)


@yorm.attr(items=List.of_type(Object))
@yorm.sync("data/images/cache.yml")
class Cache:

    SIZE = 100

    def __init__(self):
        self.items = []

    def add(self, **kwargs):
        if kwargs in self.items:
            log.debug("Already cached: %s", kwargs)
            return
        if kwargs['key'] == 'custom':
            log.debug("Skipped caching of custom background: %s", kwargs)
            return
        if profanityfilter.is_profane(kwargs['path']):
            log.debug("Skipped caching of profane content: %s", kwargs)
            return

        log.info("Caching: %s", kwargs)

        self.items.insert(0, kwargs)
        while len(self.items) > self.SIZE:
            self.items.pop()

        yorm.save(self)

    def get(self, index):
        log.info("Getting cache index: %s", index)

        try:
            data = self.items[index]
        except IndexError:
            data = {}

        log.info("Retrieved cache: %s", data)

        return data
