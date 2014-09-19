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
    'django-treebeard',
    'django-pyscss',
    'six',
    'django-compressor>=1.3',
    'beautifulsoup4',
    'django-argonauts>=1.0.0',
]

extras_require = {
    'widgy_mezzanine': [
        'mezzanine>=1.3.0',
    ],
    'page_builder': [
        'django-filer>=0.9.6',
        'markdown',
        'bleach',
        'sorl-thumbnail>=11.12',
    ],
    'form_builder': [
        'django-extensions',
        'html2text>=3.200.3',
        'phonenumbers>=5',
    ],
}

extras_require['all'] = set(j for i in extras_require.values() for j in i)

STAGE = 'alpha'

version = (0, 3, 0, STAGE)


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
    extras_require=extras_require,
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
