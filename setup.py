#!/usr/bin/env python
from setuptools import setup
import os

__doc__ = """
Widgy widgy widgy
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'mezzanine >= 1.3.0',
    'django-fusionbox',
    'django-treebeard',
    'South',
    'PyScss==1.1.3',
]

version = '0.0.1'

setup(
    name='widgy',
    version=version,
    description=__doc__,
    long_description=read('README'),
    packages=['widgy'],
    install_requires=install_requires,
    dependency_links=[
        'http://github.com/fusionbox/django-fusionbox/tarball/master#egg=django-fusionbox-0.0.2'
    ],
)
