import shutil
import os

import pytest

# This is here instead of pytest.ini because it can't be overridden from the
# environ if specified there.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

from django.conf import settings


def teardown_assets_directory():
    shutil.rmtree(settings.TEMP_DIR)


@pytest.fixture(scope="session", autouse=True)
def assets_directory(request):
    request.addfinalizer(teardown_assets_directory)


def get_collect_ignore():
    mapping = {
        'widgy.contrib.widgy_mezzanine': ['widgy/contrib/widgy_mezzanine/'],
        'widgy.contrib.form_builder': ['widgy/contrib/form_builder/'],
        'widgy.contrib.page_builder': ['widgy/contrib/page_builder/'],
        'widgy.contrib.urlconf_include': ['widgy/contrib/urlconf_include/'],
        'widgy.contrib.widgy_i18n': ['widgy/contrib/urlconf_include/'],
    }


    acc = []
    for app, path_list in mapping.items():
        if app not in settings.INSTALLED_APPS:
            acc.extend(path_list)
    return acc

collect_ignore = get_collect_ignore()
