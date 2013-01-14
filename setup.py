#!/usr/bin/env python
from setuptools import setup
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
    'South',
    'PyScss >= 1.1.4',
    'six',
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
    packages=[
        'widgy',
        'widgy.templatetags',
        'widgy.db',
        'widgy.migrations',
        'widgy.contrib',
        'widgy.contrib.form_builder',
        'widgy.contrib.widgy_mezzanine',
        'widgy.contrib.list_content_widget',
        'widgy.contrib.replacements',
        'widgy.contrib.cms',
        'widgy.contrib.page_builder',
        'widgy.contrib.form_builder.migrations',
        'widgy.contrib.widgy_mezzanine.migrations',
        'widgy.contrib.replacements.migrations',
        'widgy.contrib.cms.migrations',
        'widgy.contrib.page_builder.db',
        'widgy.contrib.page_builder.migrations',
        'widgy.contrib.page_builder.forms'
    ],
    install_requires=install_requires,
    dependency_links=[
        'http://github.com/fusionbox/django-fusionbox/tarball/master#egg=django-fusionbox-0.0.2',
        'http://github.com/Kronuz/pyScss/tarball/master#egg=pyscss-1.1.4',
    ],
    zip_safe=False,
    include_package_data=True,
)
