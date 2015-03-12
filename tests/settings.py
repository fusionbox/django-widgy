import os
import sys
import excavator
import dj_database_url
import django

try:
    import six
except ImportError:
    from django.utils import six

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
    "modeltests.core_tests",
    "modeltests.proxy_gfk",
    "regressiontests.utilstests",
    # tests/modeltests/core_tests/models::ReviewedVersionedPage has an fk to
    # `review_queue.ReviewedVersionTracker`.  Until that test is moved into a
    # contrib test suite, that app neeeds to be installed.
    "widgy.contrib.review_queue",
]

if django.VERSION < (1, 7):
    INSTALLED_APPS.append("south")


SOUTH_TESTS_MIGRATE = excavator.env_bool('SOUTH_TESTS_MIGRATE', default=False)

try:
    import easy_thumbnails
except ImportError:
    pass
else:
    if easy_thumbnails.VERSION >= 2:
        SOUTH_MIGRATION_MODULES = {
            'easy_thumbnails': 'easy_thumbnails.south_migrations',
        }

URLCONF_INCLUDE_CHOICES = tuple()
TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

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

TEMP_DIR = excavator.env_string('DJANGO_TEST_TEMP_DIR', required=True)

ROOT_URLCONF = 'urls'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(TEMP_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(TEMP_DIR, 'media')
TEMPLATE_DIRS = (os.path.join(RUNTESTS_DIR, TEST_TEMPLATE_DIR),)
USE_I18N = True
LANGUAGE_CODE = 'en'
LOGIN_URL = 'django.contrib.auth.views.login'

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

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

# Widgy Settings
WIDGY_MEZZANINE_SITE = 'modeltests.core_tests.widgy_config.widgy_site'

DAISYDIFF_JAR_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'bin', 'daisydiff', 'daisydiff.jar',
)
