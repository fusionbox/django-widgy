#!/usr/bin/env python
from setuptools import setup, find_packages
import subprocess
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
    'django-filer==0.9.4a1.dev1',
    'South',
    'PyScss == 1.1.5',
    'six',
    'markdown',
    'django-compressor',
]

version = (0, 0, 1, 'alpha')


def get_version():
    number = '.'.join(map(str, version[:3]))
    stage = version[3]
    if stage == 'final':
        return number
    elif stage == 'alpha':
        process = subprocess.Popen('git rev-parse HEAD'.split(), stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return number + '-' + stdout.strip()[:8]

setup(
    name='widgy',
    version=get_version(),
    description=__doc__,
    long_description=read('README'),
    packages=[package for package in find_packages() if package.startswith('widgy')],
    install_requires=install_requires,
    dependency_links=[
        'http://github.com/fusionbox/django-fusionbox/tarball/master#egg=django-fusionbox-0.0.2',
        'http://github.com/fusionbox/pyScss/tarball/master#egg=pyscss-1.1.5',
        'http://github.com/fusionbox/django-filer/tarball/feature/django-1.5-compat#egg=django-filer-0.9.4a1.dev1',
    ],
    zip_safe=False,
    include_package_data=True,
)
