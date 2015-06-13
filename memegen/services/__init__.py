from abc import ABCMeta


class Exceptions:

    def __init__(self, missing=KeyError):
        self.missing = missing


class Service(metaclass=ABCMeta):

    """Base class for domain services."""

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()


from . import image, link, template
