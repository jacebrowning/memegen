#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
# Copyright © 2016, Jace Browning
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Source: https://github.com/jacebrowning/verchew
# Documentation: https://verchew.readthedocs.io
# Package: https://pypi.org/project/verchew


from __future__ import unicode_literals

import os
import sys
import argparse
try:
    import configparser  # Python 3
except ImportError:
    import ConfigParser as configparser  # Python 2
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT
import logging

__version__ = '1.3'

PY2 = sys.version_info[0] == 2
CONFIG_FILENAMES = [
    'verchew.ini',
    '.verchew.ini',
    '.verchewrc',
    '.verchew',
]
SAMPLE_CONFIG = """
[Python]

cli = python
versions = Python 3.5 | Python 3.6

[Legacy Python]

cli = python2
version = Python 2.7

[virtualenv]

cli = virtualenv
version = 15.
message = Only required with Python 2.

[Make]

cli = make
version = GNU Make
optional = true

""".strip()
STYLE = {
    "~": "✔",
    "*": "⭑",
    "?": "⚠",
    "x": "✘",
}
COLOR = {
    "x": "\033[91m",  # red
    "~": "\033[92m",  # green
    "?": "\033[93m",  # yellow
    "*": "\033[94m",  # cyan
    None: "\033[0m",  # reset
}

log = logging.getLogger(__name__)


def main():
    args = parse_args()
    configure_logging(args.verbose)

    log.debug("PWD: %s", os.getenv('PWD'))
    log.debug("PATH: %s", os.getenv('PATH'))

    path = find_config(args.root, generate=args.init)
    config = parse_config(path)

    if not check_dependencies(config) and args.exit_code:
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()

    version = "%(prog)s v" + __version__
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('-r', '--root', metavar='PATH',
                        help="specify a custom project root directory")
    parser.add_argument('--init', action='store_true',
                        help="generate a sample configuration file")
    parser.add_argument('--exit-code', action='store_true',
                        help="return a non-zero exit code on failure")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="enable verbose logging")

    args = parser.parse_args()

    return args


def configure_logging(count=0):
    if count == 0:
        level = logging.WARNING
    elif count == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def find_config(root=None, filenames=None, generate=False):
    root = root or os.getcwd()
    filenames = filenames or CONFIG_FILENAMES

    path = None
    log.info("Looking for config file in: %s", root)
    log.debug("Filename options: %s", ", ".join(filenames))
    for filename in os.listdir(root):
        if filename in filenames:
            path = os.path.join(root, filename)
            log.info("Found config file: %s", path)
            return path

    if generate:
        path = generate_config(root, filenames)
        return path

    msg = "No config file found in: {0}".format(root)
    raise RuntimeError(msg)


def generate_config(root=None, filenames=None):
    root = root or os.getcwd()
    filenames = filenames or CONFIG_FILENAMES

    path = os.path.join(root, filenames[0])

    log.info("Generating sample config: %s", path)
    with open(path, 'w') as config:
        config.write(SAMPLE_CONFIG + '\n')

    return path


def parse_config(path):
    data = OrderedDict()

    log.info("Parsing config file: %s", path)
    config = configparser.ConfigParser()
    config.read(path)

    for section in config.sections():
        data[section] = OrderedDict()
        for name, value in config.items(section):
            data[section][name] = value

    for name in data:
        versions = data[name].get('versions', data[name].pop('version', ""))
        data[name]['versions'] = versions
        data[name]['patterns'] = [v.strip() for v in versions.split('|')]

    return data


def check_dependencies(config):
    success = []

    for name, settings in config.items():
        show("Checking for {0}...".format(name), head=True)
        output = get_version(settings['cli'], settings.get('cli_version_arg'))

        for pattern in settings['patterns']:
            if match_version(pattern, output):
                show(_("~") + " MATCHED: {0}".format(pattern))
                success.append(_("~"))
                break
        else:
            if settings.get('optional'):
                show(_("?") + " EXPECTED: {0}".format(settings['versions']))
                success.append(_("?"))
            else:
                show(_("x") + " EXPECTED: {0}".format(settings['versions']))
                success.append(_("x"))
            if settings.get('message'):
                show(_("*") + " MESSAGE: {0}".format(settings['message']))

    show("Results: " + " ".join(success), head=True)

    return _("x") not in success


def get_version(program, argument=None):
    argument = argument or '--version'
    args = [program, argument]

    show("$ {0}".format(" ".join(args)))
    output = call(args)
    show(output.splitlines()[0])

    return output


def match_version(pattern, output):
    return output.startswith(pattern) or " " + pattern in output


def call(args):
    try:
        process = Popen(args, stdout=PIPE, stderr=STDOUT)
    except OSError:
        log.debug("Command not found: %s", args[0])
        output = "sh: command not found: {0}".format(args[0])
    else:
        raw = process.communicate()[0]
        output = raw.decode('utf-8').strip()
        log.debug("Command output: %r", output)

    return output


def show(text, start='', end='\n', head=False):
    """Python 2 and 3 compatible version of print."""
    if head:
        start = '\n'
        end = '\n\n'

    if log.getEffectiveLevel() < logging.WARNING:
        log.info(text)
    else:
        formatted = (start + text + end)
        if PY2:
            formatted = formatted.encode('utf-8')
        sys.stdout.write(formatted)
        sys.stdout.flush()


def _(word, is_tty=None, supports_utf8=None, supports_ansi=None):
    """Format and colorize a word based on available encoding."""
    formatted = word

    if is_tty is None:
        is_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if supports_utf8 is None:
        supports_utf8 = sys.stdout.encoding == 'UTF-8'
    if supports_ansi is None:
        supports_ansi = sys.platform != 'win32' or 'ANSICON' in os.environ

    style_support = supports_utf8
    color_support = is_tty and supports_ansi

    if style_support:
        formatted = STYLE.get(word, word)

    if color_support and COLOR.get(word):
        formatted = COLOR[word] + formatted + COLOR[None]

    return formatted


if __name__ == '__main__':  # pragma: no cover
    main()
