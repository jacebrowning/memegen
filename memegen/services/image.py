import logging

from ..domain import Image, Font

from ._base import Service


log = logging.getLogger(__name__)


class ImageService(Service):

    def __init__(self, template_store, font_store, image_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store
        self.font_store = font_store
        self.image_store = image_store

    def create(self, template, text, style=None, font=None):
        font = font or self.font_store.find(Font.DEFAULT)

        image = Image(template, text, style=style, font=font)

        try:
            self.image_store.create(image)
        except OSError as exception:
            if "name too long" in str(exception):
                exception = self.exceptions.FilenameTooLong
            elif "image file" in str(exception):
                exception = self.exceptions.InvalidImageLink
            raise exception from None
        except SystemError as exception:
            log.warning(exception)
            raise self.exceptions.InvalidImageLink from None

        return image
