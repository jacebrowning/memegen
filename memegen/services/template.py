from . import Service


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
