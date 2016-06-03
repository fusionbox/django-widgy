#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import sys

__doc__ = """
A CMS framework for Django built on a heterogenous tree editor.
"""


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# In install_requires and test_requires, 'foo' should come after 'foo-*' (eg
# django should come after django-treebeard). See
# <https://bitbucket.org/pypa/setuptools/issue/196/tests_require-pytest-pytest-cov-breaks>.
install_requires = [
    'django-treebeard',
    'django-pyscss>=2.0.0',
    'six',
    'django-compressor>=1.3',
    'beautifulsoup4',
    'django-argonauts>=1.1.4',
    'Django>=1.7',
]

# Markdown stops support for Python 2.6 in version 2.5
if sys.version_info < (2, 7):
    install_requires.append('markdown<2.5')
else:
    install_requires.append('markdown')


extras_require = {
    'widgy_mezzanine': [
        'mezzanine>=4.0.0',
    ],
    'page_builder': [
        'django-filer>=0.9.10',
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

data_files = [
    ('bin/daisydiff', [
        'bin/daisydiff/daisydiff.jar',
        'bin/daisydiff/LICENSE.txt',
        'bin/daisydiff/NOTICE.txt',
        'bin/daisydiff/README.txt'
    ]),
]

extras_require['all'] = set(j for i in extras_require.values() for j in i)


setup(
    name='django-widgy',
    version='0.8.4',
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
    tests_require=['mock', 'dj-database-url', 'pytest-django', 'pytest'],
    cmdclass={'test': PyTest},
    data_files=data_files,
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
