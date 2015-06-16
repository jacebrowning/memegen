from abc import ABCMeta


class Exceptions:

    def __init__(self, not_found=KeyError, bad_code=ValueError):
        self.not_found = not_found
        self.bad_code = bad_code


class Service(metaclass=ABCMeta):

    """Base class for domain services."""

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()
