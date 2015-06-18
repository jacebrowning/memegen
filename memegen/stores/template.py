import os
import glob

import yorm

from ..domain import Template


@yorm.attr(all=yorm.converters.String)
class Aliases(yorm.converters.List):
    """A list of aliases to be used as a template's key."""


class TemplateStore:

    def __init__(self, root):
        self.root = root

        @yorm.attr(key=yorm.converters.String,
                   name=yorm.converters.String,
                   link=yorm.converters.String,
                   aliases=Aliases)
        @yorm.sync("{self.root}/{self.key}/config.yml", auto=False)
        class Model(Template):
            """Persistence model for templates."""

        self.model = Model
        self._items = {}

    def read(self, key=None):
        self._load()
        if key is None:
            return self._items.values()
        else:
            try:
                return self._items[key]
            except KeyError:
                return None

    def _load(self):
        self._items = {}
        for key in os.listdir(self.root):
            if not key.startswith('.'):
                model = self.model(key, root=self.root)
                yorm.update_object(model)
                self._items[key] = model
