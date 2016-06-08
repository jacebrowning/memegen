import logging

from ._base import Service


log = logging.getLogger(__name__)


class FontService(Service):

    def __init__(self, font_store, **kwargs):
        super().__init__(**kwargs)
        self.font_store = font_store

    def all(self):
        """Get all fonts."""
        fonts = self.font_store.all()
        return fonts
