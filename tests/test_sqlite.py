# This is an example test settings file for use with the Django test suite.
#
# The 'sqlite3' backend requires only the ENGINE setting (an in-
# memory database will be used). All other backends will require a
# NAME and potentially authentication information. See the
# following section in the docs for more information:
#
# https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/
#
# The different databases that Django supports behave differently in certain
# situations, so it is recommended to run the test suite against as many
# database backends as possible.  You may want to create a separate settings
# file for each of the backends you test against.
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
    },
}

SECRET_KEY = "widgy_tests_secret_key"
# To speed up tests under SQLite we use the MD5 hasher as the default one. 
# This should not be needed under other databases, as the relative speedup
# is only marginal there.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)

SOUTH_TESTS_MIGRATE = os.environ.get('SOUTH_TESTS_MIGRATE', False)

URLCONF_INCLUDE_CHOICES = tuple()
TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
