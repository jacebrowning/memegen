import os

import yorm

from ..domain import Template


@yorm.attr(all=yorm.types.String)
class StringList(yorm.types.List):
    pass


@yorm.attr(key=yorm.types.String)
@yorm.attr(name=yorm.types.String)
@yorm.attr(default=StringList)
@yorm.attr(link=yorm.types.String)
@yorm.attr(aliases=StringList)
@yorm.attr(regexes=StringList)
@yorm.sync("{self.root}/{self.key}/config.yml")
class TemplateModel:
    """Persistence model for templates."""

    def __init__(self, key, root):
        self.key = key
        self.root = root

    @property
    def domain(self):
        # pylint: disable=no-member
        return Template(
            key=self.key,
            name=self.name,
            lines=self.default,
            aliases=self.aliases,
            patterns=self.regexes,
            link=self.link,
            root=self.root,
        )


def load_before(func):
    def wrapped(self, *args, **kwargs):
        # pylint: disable=protected-access
        if self._items is None:
            self._load()
        return func(self, *args, **kwargs)
    return wrapped


class TemplateStore:

    def __init__(self, root):
        self.root = root
        self._items = None

    @load_before
    def read(self, key):
        try:
            model = self._items[key]
        except KeyError:
            return None
        else:
            return model.domain

    @load_before
    def filter(self, **_):
        templates = []
        for model in self._items.values():
            templates.append(model.domain)
        return templates

    def _load(self):
        self._items = {}
        for key in os.listdir(self.root):
            if key[0] not in ('.', '_'):
                model = TemplateModel(key, self.root)
                self._items[key] = model
