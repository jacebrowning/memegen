import base64

from ._base import Service


class LinkService(Service):

    def __init__(self, template_store, **kwargs):
        super().__init__(**kwargs)
        self.template_store = template_store

    @staticmethod
    def encode(key, path):
        slug = '\t'.join((key, path))
        while len(slug) % 3:
            slug += '\t'
        code = base64.urlsafe_b64encode(slug.encode('utf-8'))
        return code

    def decode(self, code):
        try:
            slug = base64.urlsafe_b64decode(code).decode('utf-8')
            key, path = slug.strip('\t').split('\t')
        except ValueError:
            raise self.exceptions.InvalidMaskedCode
        else:
            return key, path
