# Django settings for mong project.
# -*- coding: utf-8 -*-

import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

def rel(path):
    return os.path.join(PROJECT_ROOT, path)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': rel('db.sqlite'),  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'
_ = lambda s: s
LANGUAGES = (
   ('ru', _('Russian')),
   ('en', _('English')),
)
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = rel('uploads')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (
    rel('media'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
FILEBROWSE_DIRECTORY = 'uploads'
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ylh11rtk_8!wpd8e=v)0^5*#@pd%nc_6czkd+kfdvk&amp;n&amp;#wuo4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'apps.core.context_processors.global_settings',
    'apps.core.context_processors.global_referer',
    'apps.core.context_processors.template',
    'apps.catalog.context_processors.cart',
    'apps.catalog.context_processors.services',
    'apps.catalog.context_processors.stats',
    'apps.catalog.context_processors.votes',
    # 'apps.accounts.context_processors.stats',
    'apps.geo.context_processors.geoip',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


ROOT_URLCONF = 'urls'
# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    rel('templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'apps.usr',
    'apps.core',
    'apps.accounts',
    'apps.catalog',
    'apps.sms',
    'apps.geo',
    'apps.blog',
    'apps.pages',
    'apps.banner',
    'south',
    'grappelli',
    'filebrowser',
    'sorl.thumbnail',
    'cart',
    # 'djcelery',
    'pytils',
    # Uncomment the next line to enable the admin:
    'django_ipgeobase',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
GEOIP_PATH = rel('media/geo')
LOCALE_PATHS = (
    rel('conf/locale'),
)
# CONFIGURE default template
ALLOW_SUPERUSER_VOTE = False
DISALLOW_NON_UNIQUE_PHONES = False
NOT_CONFIRMED_INTERVAL = dict(hours=0, minutes=15)
INVITE_EXPIRES_HOURS = 24 * 356  # one month
HIDE_REJECTED_FROM_PARTNER = False
BRUTEFORCE_ITER = 100
HUNDRED = 100
DEFAULT_TEMPLATE = 'base_web.html'
OBJECTS_ON_PAGE = 20
SPECIALS_OBJECTS_ON_PAGE = 9
ITEMS_ON_PAGE = OBJECTS_ON_PAGE
DEFAULT_THUMBNAIL_SIZE = '150x70'
SITE_URL = 'http://localhost:8000'
SITE_SHORT_URL = 'localhost:8000'
INVITES_LIMIT_ENABLE = False
RESOURCE_NAME = u'RESOURCE NAME'
SERVICE_NAME = RESOURCE_NAME
ITEM_THUMBNAIL_SIZE = '294x216'
ITEM_THUMBNAIL_SIZE_SMALL = '180x132'
ITEM_THUMBNAIL_SIZE_TINY = '95x70'
ITEM_THUMBNAIL_SIZE_TOPBAR = '180x132'
ITEM_SERVICE_THUMBNAIL_SIZE_SMALL = '70x50'
ITEM_THUMBNAIL_SIZE_TOPBAR = '50x35'
SPECIAL_ITEM_THUMBNAIL_SIZE = 'x75'
BANNER_THUMBNAIL_SIZE = '312x132'
SERVICE_THUMBNAIL_LOGO_SIZE = '150x150'
DEFAULT_EXCHANGE_RATE_RUR = 0.1
DEFAULT_EXCHANGE_RATE = DEFAULT_EXCHANGE_RATE_RUR
BONUS_EXCHANGE_RATE = DEFAULT_EXCHANGE_RATE
DEFAULT_BONUS_PAY_THRESHOLD_AMOUNT = 0.1  # 10%
BONUS_MAX_DISCOUNT = DEFAULT_BONUS_PAY_THRESHOLD_AMOUNT
DEFAULT_PAGES_COUNT = 20
PARTNER_ORDER_ITEM_MESSAGES_WARNING = False
# 20 bonus points every 100 spent RURs
DEFAULT_BONUS_RATE = 20
DEFAULT_BONUS_RATE_THRESHOLD = 100
MBONUS_RATE_THRESHOLD = 0.01  # for multipling
BONUS_RATE = DEFAULT_BONUS_RATE
BONUS_RATE_THRESHOLD = DEFAULT_BONUS_RATE_THRESHOLD
BONUS_PER_VOTE_AMOUNT = 50
BONUS_PER_INVITE_ORDER = 500
FIRST_ORDER_BONUS = 500
REGISTER_BONUS = 500
FIRST_USER_ORDER_BONUS_ENABLE = False
REGISTER_BONUS_ENABLE = True
COMMISSION_RATE = '0.1'  # 10%, string python2.6 compability
MAX_RADIUS_SEARCH = 5000  # in meters
SAUSAGE_SCROLL_ENABLE = True
VOTES_POPUP_ENABLE = False
SEND_VOTE_SMS_ACTIVE = False
# DengiOnline
DO_PROJECT_ID = 2946
# decorators
# SMS
SMS_ENABLE = True
SEND_EMAIL = True
SMS_PROVIDERS = ('disms', 'smsdirect', 'smstwo')
SMS_PROVIDER = 'disms'
DI_SMS_URL = 'https://cabinet.di-sms.ru/smsapi.php'
SMS_TWO_URL = ''
SMS_TWO_USER = ''
SMS_DIRECT_USER = ''
SMS_DIRECT_URL = ''
SMS_FROM = 'Uzevezu'
DI_SMS_USER = 'uzevezu'
TEST_500_ENABLE = False
# CELERY SETTINGS
CELERY_TASK_RESULT_EXPIRES = 18000  # 5hours
CELERND_TASK_ERROR_EMAILS = True
# rabbitmq implementation
BROKER_HOST = 'rabbit'
BROKER_PORT = 5672
CELERY_IMPORTS = ('apps.sms.utils',)
# CELERYBEAT_SCHEDULER='djcelery.schedulers.DatabaseScheduler'
# CELERY_RESULT_BACKEND='amqp'
# SPHINX SETTINGS
SPHINX_HOST = 'localhost'
SPHINX_PORT = 9336
SPHINX_ROOT = rel('conf/sphinx')
SPHINX_CONFIG_TEMPLATE = 'sphinx/sphinx.conf'
SPHINX_API_VERSION = 0x116

#Django Debug Toolbar

INTERNAL_IPS = ('127.0.0.1', '88.201.246.190', '95.161.250.160', )
INSTALLED_APPS += (
    'debug_toolbar',
)
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    # 'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    # 'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
# import djcelery
# djcelery.setup_loader()

SERIALIZATION_MODULES = {
    'csv': 'apps.django_snippets.2240_csv_serializer',
}

CATALOG_ORDER_BY = ('cost', 'container__mean_rating',)

PROFILE_LOG_BASE = PROJECT_ROOT + '/logs/profile/'

