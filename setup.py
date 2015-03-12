#!/usr/bin/env python
from setuptools import setup, find_packages
import subprocess
import os
import sys

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

# Markdown stops support for Python 2.6 in version 2.5
if sys.version_info < (2, 7):
    install_requires.append('markdown<2.5')
else:
    install_requires.append('markdown')


extras_require = {
    'widgy_mezzanine': [
        'mezzanine>=3.1.10',
    ],
    'page_builder': [
        'django-filer>=0.9.9',
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


setup(
    name='django-widgy',
    version='0.4.0',
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
