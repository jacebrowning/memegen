from abc import ABCMeta


class Exceptions:

    def __init__(self, **kwargs):
        self.TemplateNotFound = kwargs.get('TemplateNotFound', KeyError)
        self.InvalidMaskedCode = kwargs.get('InvalidMaskedCode', ValueError)
        self.FilenameTooLong = kwargs.get('FilenameTooLong', ValueError)


class Service(metaclass=ABCMeta):

    """Base class for domain services."""

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()
