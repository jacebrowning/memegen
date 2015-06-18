from .. import domain

from . import Service


class ImageService(Service):

    def __init__(self, template_store, image_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store
        self.image_store = image_store

    def find_template(self, template):
        template = self.template_store.read(template)
        if not template:
            raise self.exceptions.not_found
        return template

    def create_image(self, template, text):
        template = self.find_template(template)
        image = domain.Image.from_template(template, text)
        return image
