#! /usr/bin/env python
import os
import shutil
import sys
import tempfile

try:
    import six
except ImportError:
    from django.utils import six


TEMP_DIR = tempfile.mkdtemp(prefix='django_')
os.environ['DJANGO_TEST_TEMP_DIR'] = TEMP_DIR


def get_contrib_test_modules():
    from django.conf import settings
    return tuple((
        module.split('.')[-1] for module in settings.INSTALLED_APPS if module.startswith('widgy.contrib')
    ))


def teardown():
    # Removing the temporary TEMP_DIR. Ensure we pass in unicode
    # so that it will successfully remove temp trees containing
    # non-ASCII filenames on Windows. (We're assuming the temp dir
    # name itself does not contain non-ASCII characters.)
    shutil.rmtree(six.text_type(TEMP_DIR))


def django_tests(verbosity, interactive, failfast, test_labels):
    import django
    from django.conf import settings

    if hasattr(django, 'setup'):
        # Django >= 1.7 requires this for setting up the application.
        django.setup()

    if django.VERSION < (1, 7):
        # must be imported after settings are set up
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    if not test_labels:
        # apps to test
        test_labels = CORE_TEST_MODULES + get_contrib_test_modules()

    test_runner = TestRunner(verbosity=verbosity, interactive=interactive,
                             failfast=failfast)
    failures = test_runner.run_tests(test_labels)

    teardown()
    return failures


CONTRIB_TEST_MODULES = (
    'form_builder',
    'page_builder',
    'review_queue',
    'urlconf_include',
    'widgy_i18n',
    'widgy_mezzanine',
)


CORE_TEST_MODULES = (
    'core_tests',
    'proxy_gfk',
    'utilstests',
    'widgy',
)


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
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif "DJANGO_SETTINGS_MODULE" not in os.environ:
        options.settions = os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    else:
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']

    if options.liveserver is not None:
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = options.liveserver

    failures = django_tests(int(options.verbosity), options.interactive,
                            options.failfast, args)
    if failures:
        sys.exit(bool(failures))
