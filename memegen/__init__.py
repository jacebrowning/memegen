"""Package for MemeGen."""

import sys

__project__ = 'MemeGen'
__version__ = '4.1'

VERSION = "{} v{}".format(__project__, __version__)

PYTHON_VERSION = 3, 5

if sys.version_info < PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))
