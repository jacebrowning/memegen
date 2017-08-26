import logging

import yorm
from yorm.types import List, Object
import profanityfilter


log = logging.getLogger(__name__)


@yorm.attr(items=List.of_type(Object))
@yorm.sync("data/cache/{self.name}.yml", auto_resolve=True)
class Cache:

    SIZE = 100

    def __init__(self, filtered=True):
        self.items = []
        self.disabled = False
        self.filtered = filtered

    @property
    def name(self):
        return 'filtered' if self.filtered else 'unfiltered'

    def add(self, **kwargs):
        if self._skip_cache(kwargs):
            return

        log.info("Caching: %s", kwargs)

        self.items.insert(0, kwargs)
        while len(self.items) > self.SIZE:
            self.items.pop()

    def get(self, index):
        log.info("Getting cache index: %s", index)

        try:
            data = self.items[index]
        except IndexError:
            data = {}

        log.info("Retrieved cache: %s", data)

        return data

    def _skip_cache(self, kwargs):
        if self.disabled:
            log.debug("Caching disabled")
            return True

        if kwargs in self.items:
            log.debug("Already cached: %s", kwargs)
            return True

        if self.filtered:

            if kwargs['key'] == 'custom' or kwargs.get('alt'):
                log.debug("Skipped caching of custom background: %s", kwargs)
                return True
            if profanityfilter.is_profane(kwargs['path']):
                log.debug("Skipped caching of profane content: %s", kwargs)
                return True

        return False
