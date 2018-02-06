import logging

from ._base import Service
from ..domain import Template, Placeholder


log = logging.getLogger(__name__)


class TemplateService(Service):

    def __init__(self, template_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store

    def all(self):
        """Get all templates."""
        templates = self.template_store.filter()
        return templates

    def find(self, key, *, allow_missing=False):  # pylint: disable=inconsistent-return-statements
        """Find a template with a matching key."""

        # Find an exact match
        key2 = Template.strip(key, keep_special=True)
        template = self.template_store.read(key2)
        if template:
            return template

        # Else, find an alias match
        key2 = Template.strip(key2)
        for template in self.all():
            if key2 in template.aliases_stripped:
                return template

        # Else, no match
        if allow_missing:
            return Placeholder(key)

        raise self.exceptions.TemplateNotFound

    def aliases(self, query=None):
        """Get all aliases with an optional name filter."""
        names = []
        for template in self.all():
            for name in [template.key] + template.aliases:
                if query is None or query in name:
                    names.append(name)
        return names

    def validate(self):
        """Ensure all templates are valid and conflict-free."""
        templates = self.all()
        keys = {template.key: template for template in templates}
        for template in templates:
            log.info("Checking template '%s' ...", template)
            if not template.validate():
                return False
            for alias in template.aliases:
                log.info("Checking alias '%s' -> '%s' ...", alias, template.key)
                if alias not in template.aliases_lowercase:
                    msg = "Alias '%s' should be lowercase characters or dashes"
                    log.error(msg, alias)
                    return False
                try:
                    existing = keys[alias]
                except KeyError:
                    keys[alias] = template
                else:
                    msg = "Alias '%s' already used in template: %s"
                    log.error(msg, alias, existing)
                    return False
        return True
