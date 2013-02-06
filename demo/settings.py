# Django settings for demo project.
import os
import socket
import re

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

HOST_NAME = socket.gethostname()

######################
# MEZZANINE SETTINGS #
######################

# The following settings are already defined in mezzanine.conf.defaults
# with default values, but are common enough to be put here, commented
# out, for convenient overriding.

# Controls the ordering and grouping of the admin menu.
#
# ADMIN_MENU_ORDER = (
#     ("Content", ("pages.Page", "blog.BlogPost",
#        "generic.ThreadedComment", ("Media Library", "fb_browse"),)),
#     ("Site", ("sites.Site", "redirects.Redirect", "conf.Setting")),
#     ("Users", ("auth.User", "auth.Group",)),
# )

# A three item sequence, each containing a sequence of template tags
# used to render the admin dashboard.
#
# DASHBOARD_TAGS = (
#     ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
#     ("comment_tags.recent_comments",),
#     ("mezzanine_tags.recent_actions",),
# )

# A sequence of fields that will be injected into Mezzanine's (or any
# library's) models. Each item in the sequence is a four item sequence.
# The first two items are the dotted path to the model and its field
# name to be added, and the dotted path to the field class to use for
# the field. The third and fourth items are a sequence of positional
# args and a dictionary of keyword args, to use when creating the
# field instance. When specifying the field class, the path
# ``django.models.db.`` can be omitted for regular Django model fields.
#
# EXTRA_MODEL_FIELDS = (
#     (
#         # Dotted path to field.
#         "mezzanine.blog.models.BlogPost.image",
#         # Dotted path to field class.
#         "somelib.fields.ImageField",
#         # Positional args for field class.
#         ("Image",),
#         # Keyword args for field class.
#         {"blank": True, "upload_to": "blog"},
#     ),
#     # Example of adding a field to *all* of Mezzanine's content types:
#     (
#         "mezzanine.pages.models.Page.another_field",
#         "IntegerField", # 'django.db.models.' is implied if path is omitted.
#         ("Another name",),
#         {"blank": True, "default": 1},
#     ),
# )

# Setting to turn on featured images for blog posts. Defaults to False.
#
# BLOG_USE_FEATURED_IMAGE = True
BLOG_URLS_ENABLED = False

# If ``True``, users will be automatically redirected to HTTPS
# for the URLs specified by the ``SSL_FORCE_URL_PREFIXES`` setting.
#
# SSL_ENABLED = True

# Host name that the site should always be accessed via that matches
# the SSL certificate.
#
# SSL_FORCE_HOST = "www.example.com"

# Sequence of URL prefixes that will be forced to run over
# SSL when ``SSL_ENABLED`` is ``True``. i.e.
# ('/admin', '/example') would force all URLs beginning with
# /admin or /example to run over SSL. Defaults to:
#
# SSL_FORCE_URL_PREFIXES = ("/admin", "/account")

# If True, the south application will be automatically added to the
# INSTALLED_APPS setting. This setting is not defined in
# mezzanine.conf.defaults as is the case with the above settings.
USE_SOUTH = True


########################
# MAIN DJANGO SETTINGS #
########################

# People who get code error notifications.
# In the format (('Full Name', 'email@example.com'),
#                ('Full Name', 'anotheremail@example.com'))
ADMINS = (
    #('Aaron Merriam', 'amerriam@fusionbox.com'),
    ('Programmers', 'programmers@fusionbox.com'),
)
MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

# A boolean that turns on/off debug mode. When set to ``True``, stack traces
# are displayed for error pages. Should always be set to ``False`` in
# production. Best set to ``True`` in local_settings.py
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = "c6662574-a5cf-4739-b00b-d757c0b4b68306920f28-3648-40a0-bae5-efec3f36b080b061fd16-4dfb-4591-9fd3-24cdc05f0292"

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = (
        '127.0.0.1',
        '63.228.88.83',
        '209.181.77.56',
        )

# fusionbox.mail.send_markdown_mail setting
EMAIL_LAYOUT = 'mail/base.html'

# Prevent certain 404 emails
IGNORABLE_404_URLS = (
        re.compile(r'\.(php|cgi)$'),
        )

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

AUTHENTICATION_BACKENDS = ("mezzanine.core.auth_backends.MezzanineBackend",)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


#############
# DATABASES #
#############

DATABASES = {
    "default": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "sqlite_database",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}


#########
# PATHS #
#########

import os

# Full filesystem path to the project.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME

# User-uploaded files
MEDIA_ROOT = os.path.join(PROJECT_PATH, '..', 'media')
MEDIA_URL = '/media/'

# Static files
STATIC_ROOT = os.path.join(PROJECT_PATH, '..', "static")
STATIC_URL = '/static/'
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'public'),
)

SCSS_IMPORTS = [os.path.join(d, 'css') for d in STATICFILES_DIRS]
SCSS_IMPORTS.extend([
    os.path.join(PROJECT_PATH, '..', 'widgy', 'static', 'widgy', 'css'),
])
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = 'demo.urls'

# Put strings here, like "/home/html/django_templates"
# or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)


################
# APPLICATIONS #
################

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.markup",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    #"mezzanine.blog",
    #"mezzanine.forms",
    "mezzanine.pages",
    'widgy',
    'widgy.contrib.page_builder',
    'widgy.contrib.form_builder',
    'widgy.contrib.widgy_mezzanine',
    "django.contrib.admin",
    #"mezzanine.galleries",
    #"mezzanine.twitter",
    #"mezzanine.accounts",
    #"mezzanine.mobile",

    # standard fusionbox apps
    'debug_toolbar',
    'compressor',
    'fusionbox.core',
    'south',
    'django_extensions',

    # widgy apps
    'filer',
    'easy_thumbnails',
    'urlconf_include',

    # local project
    'demo.demo_widgets'
)

FORMS_LABEL_MAX_LENGTH = 255
FORMS_FIELD_MAX_LENGTH = 255

# Filer Settings
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
FILER_FILE_MODELS = (
    #'widgy.contrib.page_builder.models.WidgyImageFile',
    'filer.models.imagemodels.Image',
    'filer.models.filemodels.File',
)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "mezzanine.conf.context_processors.settings",
)

# List of middleware classes to use. Order is important; in the request phase,
# these middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE_CLASSES = (
    "mezzanine.core.middleware.UpdateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "mezzanine.core.request.CurrentRequestMiddleware",
    "mezzanine.core.middleware.TemplateForDeviceMiddleware",
    "mezzanine.core.middleware.TemplateForHostMiddleware",
    "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
    # Uncomment the following if using any of the SSL settings:
    # "mezzanine.core.middleware.SSLRedirectMiddleware",
    "urlconf_include.middleware.PatchUrlconfMiddleware",
    "mezzanine.pages.middleware.PageMiddleware",
    "mezzanine.core.middleware.FetchFromCacheMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    # prevent problems comes after transaction
    "widgy.middleware.PreventProblemsMiddleware",
)

# Store these package names here as they may change in the future since
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"


#########################
# OPTIONAL APPLICATIONS #
#########################

# These will be added to ``INSTALLED_APPS``, only if available.
OPTIONAL_APPS = (
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

# Compressor settings
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'sass {infile} {outfile}'),

    # requires pyScss
    ('text/x-scss', 'python -mscss.tool -C -o {outfile} %s' %
     ' '.join(['-I "%s"' % d for d in SCSS_IMPORTS])
     )
)


FORCE_SCRIPT_NAME = ''

REPLACEMENTS_APP_BLACKLIST = ('admin',)

WIDGY_MEZZANINE_SITE = 'demo.widgy.widgy_site'

DAISYDIFF_JAR_PATH = os.path.join(PROJECT_ROOT, '..', 'bin', 'daisydiff', 'daisydiff.jar')

###################
# DEPLOY SETTINGS #
###################

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

# FABRIC = {
#     "SSH_USER": "", # SSH username
#     "SSH_PASS":  "", # SSH password (consider key-based authentication)
#     "SSH_KEY_PATH":  "", # Local path to SSH key file, for key-based auth
#     "HOSTS": [], # List of hosts to deploy to
#     "VIRTUALENV_HOME":  "", # Absolute remote path for virtualenvs
#     "PROJECT_NAME": "", # Unique identifier for project
#     "REQUIREMENTS_PATH": "", # Path to pip requirements, relative to project
#     "GUNICORN_PORT": 8000, # Port gunicorn will listen on
#     "LOCALE": "en_US.UTF-8", # Should end with ".UTF-8"
#     "LIVE_HOSTNAME": "www.example.com", # Host for public site.
#     "REPO_URL": "", # Git or Mercurial remote repo URL for the project
#     "DB_PASS": "", # Live database password
#     "ADMIN_PASS": "", # Live admin user password
# }


##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
# Import server specific settings 'settings_<hostname>.py'
try:
    import imp, sys
    module_name = 'settings_' + HOST_NAME
    module_info = imp.find_module(module_name, [PROJECT_PATH] + sys.path)
    live_settings = imp.load_module(module_name, *module_info)
except ImportError:
    pass
else:
    try:
        attrlist = live_settings.__all__
    except AttributeError:
        attrlist = dir (live_settings)
    for attr in attrlist:
        if attr.startswith('__'):
            continue
        globals()[attr] = getattr (live_settings, attr)

try:
    from settings_local import *
except ImportError:
    pass

# This import needs to happen after settings_local import due to how the cache loads
from django.template.loader import add_to_builtins
add_to_builtins('cachebuster.templatetags.cachebuster')


DATABASE_ENGINE = DATABASES['default']['ENGINE']


####################
# DYNAMIC SETTINGS #
####################

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable.
from mezzanine.utils.conf import set_dynamic_settings
set_dynamic_settings(globals())
