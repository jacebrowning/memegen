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


watch_paths = ["memegen", "tests", "data"]


@select_runnable('python')
@file_validator
def python_files(filename):
    return filename.endswith('.py')


@select_runnable('yaml')
@file_validator
def yaml_files(filename):
    return filename.endswith('.yml')


@runnable
def python(*_):

    for count, (command, title) in enumerate((
        (('make', 'test'), "Unit Tests"),
        (('make', 'tests'), "Integration Tests"),
        (('make', 'check'), "Static Analysis"),
        (('make', 'validate'), "Meme Validation"),
        (('make', 'doc'), None),
    ), start=1):

        if not run(command, title, count):
            return False

    return True


@runnable
def yaml(*_):

    for count, (command, title) in enumerate((
        (('make', 'validate'), "Meme Validation"),
    ), start=1):

        if not run(command, title, count):
            return False

    return True


GROUP = int(time.time())  # unique per run

_show_coverage = True
_rerun_args = None


def run(command, title, count):
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

    if failure:
        _rerun_args = command, title, count

    return not failure


def show_notification(message, title):
    if notify and title:
        notify(message, title=title, group=GROUP)


def show_coverage():
    global _show_coverage

    if _show_coverage:
        subprocess.call(['make', 'read-coverage'])

    _show_coverage = False
