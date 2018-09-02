"""Package for memegen."""

import sys

__project__ = 'memegen.link'
__version__ = '5.6'

VERSION = "{} v{}".format(__project__, __version__)

PYTHON_VERSION = 3, 6

if sys.version_info < PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))
