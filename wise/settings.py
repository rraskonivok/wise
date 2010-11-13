import os

#Eagerly load the pure module to avoid an initial hiccup when a worker starts
import worksheet.pure.prelude

APPEND_SLASH = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOG_FILE = 'session.log'

# A quick note about security. *WISE IS ALPHA SOFTWARE AND NOT SECURE* (yet)
ADMINS = (
    # ('Leonhard Euler', 'leuler@unibas.ch'),
)

MANAGERS = ADMINS

# Set your database information here

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'wise.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

INSTALLED_MATH_PACKAGES = ('base','logic','calculus')

# Change to your desired cache
CACHE_BACKEND = 'db://cache'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')

MEDIA_URL = '/static'

ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = 'changeme'

INTERNAL_IPS = ('127.0.0.1',)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'middleware.SpacelessMiddleware'
)

ROOT_URLCONF = 'wise.urls'

# Template directories include:
#
# templates/
# worksheet/templates
# worksheet/$PACKAGES/templates

TEMPLATE_DIRS = tuple(
        ['templates'] +
        [('%s/templates' % pack) for pack in INSTALLED_MATH_PACKAGES]
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'wise.worksheet',
    # Gunicorn needs to be installed in site-packages or dropped
    # into the same directory as this file, if you can't run
    # ' import gunicorn ' form this directory then it will fail
    'gunicorn',
    'debug_toolbar',
    'reversion',
    'piston'
)

# Sphinx sometimes complains about paths if it is run from a
# different directory so this flag disables all the template
# precaching / path loading so that Sphinx can complete. If this
# is enabled then the worksheet will *NOT* work.
IGNORE_PATHS = False

PRECOMPILE  = False

