import base64

from . import Service


class LinkService(Service):

    def __init__(self, template_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store

    def encode(self, key, top, bottom):
        slug = '\t'.join((key, top, bottom))
        while len(slug) % 3:
            slug += ' '
        code = base64.urlsafe_b64encode(slug.encode('utf-8'))
        return code

    def decode(self, code):
        try:
            slug = base64.urlsafe_b64decode(code).decode('utf-8')
        except ValueError:
            raise self.exceptions.bad_code
        else:
            key, top, bottom = slug.strip().split('\t')
            return key, top, bottom
