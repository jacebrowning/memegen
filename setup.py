#!/usr/bin/env python

"""Setup script for the package."""

import os
import logging

import setuptools

from memegen import __project__, __version__

try:
    README = open("README.rst").read()
    CHANGELOG = open("CHANGELOG.rst").read()
except IOError:
    LONG_DESCRIPTION = "<placeholder>"
else:
    LONG_DESCRIPTION = README + '\n' + CHANGELOG


def load_requirements():
    """Exclude specific requirements based on platform."""
    requirements = []

    for line in open("requirements.txt").readlines():
        line = line.strip()
        name = line.split('=')[0].strip()

        if os.name == 'nt':
            if name in ['psycopg2', 'gunicorn']:
                logging.warning("Skipped requirement: %s", line)
                continue

        requirements.append(line)

    return requirements


setuptools.setup(
    name=__project__,
    version=__version__,

    description="The open source meme generator.",
    url='https://github.com/jacebrowning/memegen',
    author='Jace Browning',
    author_email='jacebrowning@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': []},

    long_description=LONG_DESCRIPTION,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],

    install_requires=load_requirements(),
)
