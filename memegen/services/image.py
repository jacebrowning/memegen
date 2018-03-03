import log

from ._base import Service
from ..domain import Image, Font


class ImageService(Service):

    def __init__(self, template_store, font_store, image_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store
        self.font_store = font_store
        self.image_store = image_store

    def create(self, template, text, font=None, **options):
        image = Image(
            template, text,
            font=font or self.font_store.find(Font.DEFAULT),
            watermark_font=self.font_store.find(Font.WATERMARK),
            **options,
        )

        try:
            self.image_store.create(image)
        except OSError as exception:
            if "name too long" in str(exception):
                exception = self.exceptions.FilenameTooLong
            elif "image file" in str(exception):
                exception = self.exceptions.InvalidImageLink
            raise exception  # pylint: disable=raising-bad-type
        except (ValueError, SystemError) as exception:
            log.warning(exception)
            raise self.exceptions.InvalidImageLink

        return image
