from . import Service


class ImageService(Service):

    def __init__(self, template_store, image_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store
        self.image_store = image_store
