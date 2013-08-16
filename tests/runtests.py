#! /usr/bin/env python
import os
import shutil
import sys
import tempfile
from operator import itemgetter

from widgy import contrib
try:
    import six
except ImportError:
    from django.utils import six


def upath(path):
    """
    Always return a unicode path.
    """
    if not six.PY3:
        fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        return path.decode(fs_encoding)
    return path

CONTRIB_DIR_NAME = 'widgy.contrib'
MODEL_TESTS_DIR_NAME = 'modeltests'
REGRESSION_TESTS_DIR_NAME = 'regressiontests'

TEST_TEMPLATE_DIR = 'templates'

RUNTESTS_DIR = os.path.dirname(upath(__file__))
CONTRIB_DIR = os.path.dirname(upath(contrib.__file__))
MODEL_TEST_DIR = os.path.join(RUNTESTS_DIR, MODEL_TESTS_DIR_NAME)
REGRESSION_TEST_DIR = os.path.join(RUNTESTS_DIR, REGRESSION_TESTS_DIR_NAME)
TEMP_DIR = tempfile.mkdtemp(prefix='django_')
os.environ['DJANGO_TEST_TEMP_DIR'] = TEMP_DIR

REGRESSION_SUBDIRS_TO_SKIP = []

ALWAYS_INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.pages",
    "mezzanine.forms",
    # blog is affected by https://code.djangoproject.com/ticket/12728
    # "mezzanine.blog",
    "widgy",
    "treebeard",
    "compressor",
    "argonauts",
    "filer",
    "south",
]

def get_test_modules():
    modules = []
    for loc, dirpath in (
        (MODEL_TESTS_DIR_NAME, MODEL_TEST_DIR),
        (REGRESSION_TESTS_DIR_NAME, REGRESSION_TEST_DIR),
        (CONTRIB_DIR_NAME, CONTRIB_DIR)):
        for f in os.listdir(dirpath):
            if (f.startswith('__init__') or
                f.startswith('.') or
                # Python 3 byte code dirs (PEP 3147)
                f == '__pycache__' or
                f.startswith('sql') or
                os.path.basename(f) in REGRESSION_SUBDIRS_TO_SKIP):
                continue
            files = os.listdir(os.path.join(dirpath, f))
            # skip directories with no python files
            for file in files:
                if file.endswith('.py'):
                    modules.append((loc, f))
                    break
    return modules

def setup(verbosity, test_labels):
    from django.conf import settings
    state = {
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'ROOT_URLCONF': getattr(settings, "ROOT_URLCONF", ""),
        'TEMPLATE_DIRS': settings.TEMPLATE_DIRS,
        'USE_I18N': settings.USE_I18N,
        'LOGIN_URL': settings.LOGIN_URL,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'MIDDLEWARE_CLASSES': settings.MIDDLEWARE_CLASSES,
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': settings.STATIC_ROOT,
    }

    # Redirect some settings for the duration of these tests.
    settings.INSTALLED_APPS = ALWAYS_INSTALLED_APPS
    settings.ROOT_URLCONF = 'urls'
    settings.STATIC_URL = '/static/'
    settings.STATIC_ROOT = os.path.join(TEMP_DIR, 'static')
    settings.MEDIA_URL = '/media/'
    settings.MEDIA_ROOT = os.path.join(TEMP_DIR, 'media')
    settings.TEMPLATE_DIRS = (os.path.join(RUNTESTS_DIR, TEST_TEMPLATE_DIR),)
    settings.USE_I18N = True
    settings.LANGUAGE_CODE = 'en'
    settings.LOGIN_URL = 'django.contrib.auth.views.login'
    settings.MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.common.CommonMiddleware',
    )
    settings.SITE_ID = 1
    settings.WIDGY_MEZZANINE_SITE = 'modeltests.core_tests.widgy_config.widgy_site'
    settings.DAISYDIFF_JAR_PATH = os.path.join(os.path.dirname(__file__),
                                               '..', 'bin', 'daisydiff', 'daisydiff.jar')


    # mezzanine junk
    settings.PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
    from mezzanine.utils.conf import set_dynamic_settings
    set_dynamic_settings(vars(settings._wrapped))

    # mezzanine sets this to a tuple, but we need ot to be a list
    settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)

    # Load all the ALWAYS_INSTALLED_APPS.
    # (This import statement is intentionally delayed until after we
    # access settings because of the USE_I18N dependency.)
    from django.db.models.loading import get_apps, load_app
    get_apps()

    # Load all the test model apps.
    test_labels_set = set([label.split('.')[0] for label in test_labels])
    test_modules = get_test_modules()

    for module_dir, module_name in test_modules:
        module_label = '.'.join([module_dir, module_name])
        # if the module was named on the command line, or
        # no modules were named (i.e., run all), import
        # this module and add it to the list to test.
        if not test_labels or module_name in test_labels_set:
            if verbosity >= 2:
                print("Importing application %s" % module_name)
            mod = load_app(module_label)
            if mod:
                if module_label not in settings.INSTALLED_APPS:
                    settings.INSTALLED_APPS.append(module_label)

    return state

def teardown(state):
    from django.conf import settings
    # Removing the temporary TEMP_DIR. Ensure we pass in unicode
    # so that it will successfully remove temp trees containing
    # non-ASCII filenames on Windows. (We're assuming the temp dir
    # name itself does not contain non-ASCII characters.)
    shutil.rmtree(six.text_type(TEMP_DIR))
    # Restore the old settings.
    for key, value in state.items():
        setattr(settings, key, value)

def django_tests(verbosity, interactive, failfast, test_labels):
    from django.conf import settings

    state = setup(verbosity, test_labels)
    extra_tests = []

    # must be imported after settings are set up
    from south.management.commands import patch_for_test_db_setup
    patch_for_test_db_setup()

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    if not hasattr(settings, 'TEST_RUNNER'):
        settings.TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=verbosity, interactive=interactive,
        failfast=failfast)
    failures = test_runner.run_tests(test_labels, extra_tests=extra_tests)

    teardown(state)
    return failures

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options] [module module module ...]"
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-v', '--verbosity', action='store', dest='verbosity', default='1',
        type='choice', choices=['0', '1', '2', '3'],
        help='Verbosity level; 0=minimal output, 1=normal output, 2=all '
             'output')
    parser.add_option(
        '--noinput', action='store_false', dest='interactive', default=True,
        help='Tells Django to NOT prompt the user for input of any kind.')
    parser.add_option(
        '--failfast', action='store_true', dest='failfast', default=False,
        help='Tells Django to stop running the test suite after first failed '
             'test.')
    parser.add_option(
        '--settings',
        help='Python path to settings module, e.g. "myproject.settings". If '
             'this isn\'t provided, the DJANGO_SETTINGS_MODULE environment '
             'variable will be used.')
    parser.add_option(
        '--liveserver', action='store', dest='liveserver', default=None,
        help='Overrides the default address where the live server (used with '
             'LiveServerTestCase) is expected to run from. The default value '
             'is localhost:8081.'),
    options, args = parser.parse_args()
    if not args:
        # apps to test
        args = map(itemgetter(1), get_test_modules()) + ['widgy']
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("DJANGO_SETTINGS_MODULE is not set in the environment. "
                      "Set it or use --settings.")
    else:
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']

    if options.liveserver is not None:
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = options.liveserver

    failures = django_tests(int(options.verbosity), options.interactive,
                            options.failfast, args)
    if failures:
        sys.exit(bool(failures))
