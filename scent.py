"""Configuration file for sniffer."""

import os
import time
import subprocess

from sniffer.api import select_runnable, file_validator, runnable
try:
    from pync import Notifier
except ImportError:
    notify = None
else:
    notify = Notifier.notify


watch_paths = ["memegen", "tests", "scripts", "data"]


@select_runnable('python')
@file_validator
def python_files(filename):
    """Match Python source files."""

    return all(
        (filename.endswith('.py'),
        not os.path.basename(filename).startswith('.')),
    )


@runnable
def python(*_):
    """Run targets for Python."""

    for count, (command, title, retry) in enumerate((
        (('make', 'test'), "Unit Tests", True),
        (('make', 'tests'), "Integration Tests", False),
        (('make', 'check'), "Static Analysis", True),
        (('make', 'doc'), None, True),
    ), start=1):

        if not run(command, title, count, retry):
            return False

    return True


GROUP = int(time.time())  # unique per run

_show_coverage = False
_rerun_args = None


def run(command, title, count, retry):
    """Run a command-line program and display the result."""
    global _rerun_args

    if _rerun_args:
        args = _rerun_args
        _rerun_args = None
        if not run(*args):
            return False

    print("")
    print("$ %s" % ' '.join(command))
    failure = subprocess.call(command)

    if failure:
        mark = "❌" * count
        message = mark + " [FAIL] " + mark
    else:
        mark = "✅" * count
        message = mark + " [PASS] " + mark
    show_notification(message, title)

    show_coverage()

    if failure and retry:
        _rerun_args = command, title, count, retry

    return not failure


def show_notification(message, title):
    """Show a user notification."""
    if notify and title:
        notify(message, title=title, group=GROUP)


def show_coverage():
    """Launch the coverage report."""
    global _show_coverage

    if _show_coverage:
        subprocess.call(['make', 'read-coverage'])

    _show_coverage = False
