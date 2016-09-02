import logging

import yorm
from yorm.types import List, Object


log = logging.getLogger(__name__)


@yorm.attr(items=List.of_type(Object))
@yorm.sync("data/images/cache.yml")
class Cache:

    SIZE = 9

    def __init__(self):
        self.items = []

    def add(self, **kwargs):
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
