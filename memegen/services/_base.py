from abc import ABCMeta


class Exceptions:

    def __init__(self, *exceptions):
        kwargs = {e.__name__: e for e in exceptions}
        self.TemplateNotFound = kwargs.get('TemplateNotFound', KeyError)
        self.InvalidMaskedCode = kwargs.get('InvalidMaskedCode', ValueError)
        self.FilenameTooLong = kwargs.get('FilenameTooLong', ValueError)
        self.InvalidImageLink = kwargs.get('InvalidImageLink', ValueError)


class Service(metaclass=ABCMeta):
    """Base class for domain services."""

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()
