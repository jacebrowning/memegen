from ..domain import Image

from ._base import Service


class ImageService(Service):

    def __init__(self, template_store, image_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store
        self.image_store = image_store

    def create(self, template, text, style=None):
        image = Image(template, text, style=style)

        try:
            self.image_store.create(image)
        except OSError as exception:
            if "name too long" in str(exception):
                exception = self.exceptions.FilenameTooLong
            elif "image file" in str(exception):
                exception = self.exceptions.InvalidImageLink
            raise exception from None

        return image

    def get_latest(self, count):
        if count != 1:
            raise NotImplementedError("TODO: support multiple")
        return self.image_store.latest

    @property
    def latest(self):
        return self.get_latest(1)
