import shutil

import pytest
try:
    import six
except ImportError:
    from django.utils import six
from django.conf import settings


def teardown_assets_directory():
    # Removing the temporary TEMP_DIR. Ensure we pass in unicode
    # so that it will successfully remove temp trees containing
    # non-ASCII filenames on Windows. (We're assuming the temp dir
    # name itself does not contain non-ASCII characters.)
    shutil.rmtree(six.text_type(settings.TEMP_DIR))


@pytest.fixture(scope="session", autouse=True)
def assets_directory(request):
    request.addfinalizer(teardown_assets_directory)
