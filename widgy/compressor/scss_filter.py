from __future__ import absolute_import

import fnmatch
import os

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage

from compressor.conf import settings
from compressor.filters import FilterBase

import scss
from scss import config


def finder(glob):
    """
    Finds all files in the django finders for a given glob,
    returns the file path, if available, and the django storage object.
    storage objects must implement the File storage API:
    https://docs.djangoproject.com/en/dev/ref/files/storage/
    """
    for finder in finders.get_finders():
        for path, storage in finder.list([]):
            if fnmatch.fnmatchcase(path, glob):
                yield path, storage


config.STATIC_ROOT = finder
config.STATIC_URL = staticfiles_storage.url('scss/')


# Use COMPRESS_ROOT instead of STATIC_ROOT because STATIC_ROOT isn't always
# set.  This is where PyScss places the sprite files.
config.ASSETS_ROOT = os.path.join(settings.COMPRESS_ROOT, 'scss', 'assets')
# PyScss expects a trailing slash.
config.ASSETS_URL = staticfiles_storage.url('scss/assets/')

compiler = scss.Scss(
    scss_opts={
        'compress': False,
        'debug_info': False,
        # PyScss expects a list not a tuple.
        'load_paths': list(settings.SCSS_IMPORTS),
    }
)


class ScssFilter(FilterBase):
    compiler = compiler

    def __init__(self, content, attrs=None, filter_type=None, filename=None):
        # It looks like there is a bug in django-compressor because it expects
        # us to accept attrs.
        super(ScssFilter, self).__init__(content, filter_type, filename)

    def input(self, **kwargs):
        if not os.path.exists(config.ASSETS_ROOT):
            os.makedirs(config.ASSETS_ROOT)
        return self.compiler.compile(self.content)
