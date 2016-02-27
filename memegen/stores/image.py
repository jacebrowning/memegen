import os

from flask import current_app as app

from ..extensions import redis
from ..domain import Image, Text


def decode_bytstring_dict(dct):
    out = {}
    for k, v in dct.items():
        out[k.decode()] = v.decode()
    return out


class ImageStore:

    def __init__(self, root):
        self.root = root

    @property
    def latest(self):
        data = redis.hgetall('latest')
        if not data:
            raise FileNotFoundError()

        data = decode_bytstring_dict(data)

        text = Text(data['path'])

        style = data.get('style', None)
        if style == 'None':
            style = None

        template = app.template_service.find(
            data['template'],
            allow_missing=True
        )
        image = Image(template, text, style=style, root=self.root)

        return image

    def exists(self, image):
        image.root = self.root
        # TODO: add a way to determine if the styled image was already generated
        return os.path.isfile(image.path) and not image.style

    def create(self, image):
        image.root = self.root
        image.generate()
