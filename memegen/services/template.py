from . import Service


class TemplateService(Service):

    def __init__(self, template_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store
