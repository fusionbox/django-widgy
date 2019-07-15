import os
import imp
import django

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c6662574-a5cf-4739-b00b-d757c0b4b68306920f28-3648-40a0-bae5-efec3f36b080b061fd16-4dfb-4591-9fd3-24cdc05f0292'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

STATIC_ROOT = os.path.join(BASE_DIR, "demo", "static")
STATIC_URL = '/static/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.redirects',

    'mezzanine.conf',
    'mezzanine.core',
    'mezzanine.generic',
    'mezzanine.pages',
    'django_comments',
    'filebrowser_safe',
    'grappelli_safe',

    'widgy',
    'widgy.contrib.page_builder',
    'widgy.contrib.form_builder',
    'widgy.contrib.widgy_mezzanine',
    'widgy.contrib.urlconf_include',
    'widgy.contrib.review_queue',
    'widgy.contrib.widgy_i18n',

    'django.contrib.admin',

    'filer',
    'easy_thumbnails',
    'compressor',
    'scss',
    'sorl.thumbnail',
    'debug_toolbar',
    'django_extensions',
    'argonauts',

    'demo.demo_widgets',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'mezzanine.core.request.CurrentRequestMiddleware',
    'mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware',
    'mezzanine.pages.middleware.PageMiddleware',
)

PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"
TESTING = False
GRAPPELLI_INSTALLED = True
ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"
SITE_ID = 1

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'widgy.debugtoolbar.templates.TemplatePanel',
)

ROOT_URLCONF = 'demo.urls'

WSGI_APPLICATION = 'demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.5/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sqlite_database'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.5/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# review_queue request this on django < 1.5
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'demo', 'media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'demo', 'public'),
)

STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

WIDGY_ROOT = imp.find_module('widgy')[1]

COMPRESS_ENABLED = True

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
)

INTERNAL_IPS = (
    '127.0.0.1',
    '208.186.116.206',
    '208.186.142.130',
)

PAGE_MENU_TEMPLATES = (
    (1, "Top Nav", "pages/menus/dropdown.html"),
    (2, "Left Nav", "pages/menus/leftnav.html"),
    (3, "Footer", "pages/menus/footer.html"),
)

ADMIN_MENU_ORDER = [
    ('Widgy', (
        'pages.Page',
        'page_builder.Callout',
        'form_builder.Form',
        ('Review queue', 'review_queue.ReviewedVersionCommit'),
        ('File manager', 'filer.Folder'),
    )),
]

ADD_PAGE_ORDER = (
    'widgy_mezzanine.WidgyPage',
)

URLCONF_INCLUDE_CHOICES = (
    ('demo.demo_url.urls', 'Demo url'),
)

DAISYDIFF_JAR_PATH = os.path.join(WIDGY_ROOT, '..', 'bin', 'daisydiff', 'daisydiff.jar')

REQUIRE_BUILD_PROFILE = 'widgy.build.js'
REQUIRE_BASE_URL = 'widgy/js'
STATICFILES_STORAGE = 'require.storage.OptimizedStaticFilesStorage'

WIDGY_MEZZANINE_SITE = 'demo.widgysite.widgy_site'


DATABASE_ENGINE = DATABASES['default']['ENGINE']
LOGIN_URL = '/admin/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'demo', 'templates'),
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
                "mezzanine.conf.context_processors.settings",
                "mezzanine.pages.context_processors.page",
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]
