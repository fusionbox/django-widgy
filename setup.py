#!/usr/bin/env python
from setuptools import setup, find_packages
import subprocess
import os

__doc__ = """
A CMS framework for Django built on a heterogenous tree editor.
"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'mezzanine >= 3.1.10',
    'django-treebeard',
    'django-filer>=0.9.6',
    'South',
    'django-pyscss',
    'six',
    'markdown',
    'bleach',
    'django-compressor>=1.3',
    'django-extensions',
    'beautifulsoup4',
    'sorl-thumbnail>=11.12',
    'html2text>=3.200.3',
    'phonenumbers>=5',
    'django-argonauts>=1.0.0',
]

STAGE = 'final'

version = (0, 3, 2, STAGE)


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
    name='django-widgy',
    version=get_version(),
    author='Fusionbox, Inc.',
    author_email='programmers@fusionbox.com',
    description=__doc__,
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    url='http://docs.wid.gy/',
    packages=[package for package in find_packages() if package.startswith('widgy')],
    install_requires=install_requires,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
