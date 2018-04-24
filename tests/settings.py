import os
import sys
import dj_database_url
import tempfile

import six

DATABASES = {'default': dj_database_url.config(default='sqlite:///test_db.sqlite3')}

SECRET_KEY = "widgy_tests_secret_key"
# To speed up tests under SQLite we use the MD5 hasher as the default one.
# This should not be needed under other databases, as the relative speedup
# is only marginal there.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    "widgy",
    "treebeard",
    "compressor",
    "argonauts",
    # tests modules
    "tests.core_tests",
    "tests.utilstests",
    # tests/core_tests/models::ReviewedVersionedPage has an fk to
    # `review_queue.ReviewedVersionTracker`.  Until that test is moved into a
    # contrib test suite, that app neeeds to be installed.
    "widgy.contrib.review_queue",
]


URLCONF_INCLUDE_CHOICES = tuple()

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TESTING = False
SITE_ID = 1


def upath(path):
    """
    Always return a unicode path.
    """
    if not six.PY3:
        fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        return path.decode(fs_encoding)
    return path

RUNTESTS_DIR = os.path.dirname(upath(__file__))
TEST_TEMPLATE_DIR = 'templates'

# This directory is removed by /conftest.py
TEMP_DIR = tempfile.mkdtemp(prefix='widgy_')

ROOT_URLCONF = 'tests.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(TEMP_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(TEMP_DIR, 'media')

USE_I18N = True
LANGUAGE_CODE = 'en'
LOGIN_URL = '/accounts/login/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(RUNTESTS_DIR, TEST_TEMPLATE_DIR),
        ],
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

# Widgy Settings
WIDGY_MEZZANINE_SITE = 'tests.core_tests.widgy_config.widgy_site'

DAISYDIFF_JAR_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'bin', 'daisydiff', 'daisydiff.jar',
)
