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
    'django-treebeard',
    'django-filer==0.9.5',
    # We don't actually require polymorphic -- filer does. we do need to
    # increase the minimum version though, to one that supports django
    # 1.6.
    'django_polymorphic==0.5.1',
    'South',
    'PyScss == 1.1.5',
    'six',
    'markdown',
    'bleach',
    'django-compressor',
    'django-extensions',
    'beautifulsoup4',
    'sorl-thumbnail==11.12',
    'html2text==3.200.3',
    'phonenumbers>=5',
    'django-argonauts==1.0.0',
]

STAGE = 'final'

version = (0, 1, 5, STAGE)


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
    author='Fusionbox, Inc.',
    author_email='programmers@fusionbox.com',
    description=__doc__,
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    url='https://django-widgy.readthedocs.org/',
    license='BSD',
    packages=[package for package in find_packages() if package.startswith('widgy')],
    install_requires=install_requires,
    dependency_links=[
        'http://github.com/fusionbox/pyScss/tarball/master#egg=pyscss-1.1.5',
        'http://github.com/chrisglass/django_polymorphic/tarball/master#egg=django_polymorphic-0.5.1',
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
