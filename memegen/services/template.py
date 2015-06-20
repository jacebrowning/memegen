import logging

from . import Service


log = logging.getLogger(__name__)


class TemplateService(Service):

    def __init__(self, template_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store

    def all(self):
        """Get all templates."""
        templates = self.template_store.filter()
        return templates

    def find(self, key):
        """Find a template with a matching key."""
        template = self.template_store.read(key)
        if not template:
            raise self.exceptions.not_found
        return template

    def validate(self):
        """Ensure all template are valid and conflict-free."""
        templates = self.all()
        keys = {template.key: template for template in templates}
        for template in templates:
            log.info("checking template '%s' ...", template)
            if not template.validate():
                return False
            for alias in template.aliases:
                log.info("checking alias '%s' -> '%s' ...", alias, template.key)
                try:
                    existing = keys[alias]
                except KeyError:
                    keys[alias] = template
                else:
                    msg = "alias '%s' already used in template: %s"
                    log.error(msg, alias, existing)
                    return False
        return True
