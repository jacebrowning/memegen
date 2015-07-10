import os

import yorm

from ..domain import Template


@yorm.attr(all=yorm.converters.String)
class StringList(yorm.converters.List):
    pass


@yorm.attr(key=yorm.converters.String)
@yorm.attr(name=yorm.converters.String)
@yorm.attr(default=StringList)
@yorm.attr(link=yorm.converters.String)
@yorm.attr(aliases=StringList)
@yorm.sync("{self.root}/{self.key}/config.yml")
class TemplateModel:
    """Persistence model for templates."""

    def __init__(self, key, root):
        self.key = key
        self.root = root

    @staticmethod
    def pm_to_dm(model):
        template = Template(model.key)
        template.name = model.name
        template.lines = model.default
        template.aliases = model.aliases
        template.link = model.link
        template.root = model.root
        return template


def load_before(func):
    def wrapped(self, *args, **kwargs):
        # pylint: disable=W0212
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
            template = TemplateModel.pm_to_dm(model)
            return template

    @load_before
    def filter(self, **_):
        templates = []
        for model in self._items.values():
            template = TemplateModel.pm_to_dm(model)
            templates.append(template)
        return templates

    def _load(self):
        self._items = {}
        for key in os.listdir(self.root):
            if key[0] not in ('.', '_'):
                model = TemplateModel(key, self.root)
                self._items[key] = model
