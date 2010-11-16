try:
    from gevent import monkey; monkey.patch_all()
except:
    pass

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

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'wise.db'      # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# ('base') is the minimum needed to run
#INSTALLED_MATH_PACKAGES = ('base','logic','calculus')
INSTALLED_MATH_PACKAGES = ('base',)

# Change to your desired cache or disable. Initially you may need
# to run 
#`
#    python manage.py createcachetable
# 
# if you want to use a database cache
CACHE_BACKEND = 'db://cache'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')

MEDIA_URL = '/static'

# In order to use admin with gunicorn you'll need to grab the
# admin resources from your local install. Use the script
# static/copy_admin_resources.sh to do this. This script will
# build /static/admin
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Change this to something special, Django uses this to salt
# password hashes
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
ROOTDIR = os.path.abspath(os.path.dirname(__file__))

# Template directories include:
#
# templates/
# worksheet/templates
# worksheet/$PACKAGES/templates

TEMPLATE_DIRS = tuple(
        [ROOTDIR +'/templates'] +
        [ROOTDIR + ('/%s/templates' % pack) for pack in INSTALLED_MATH_PACKAGES]
)

print TEMPLATE_DIRS

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'gunicorn',

    # In order to use admin with gunicorn you'll need to grab the
    # admin resources from your local install. Use the script
    # static/copy_admin_resources.sh to do this
    'django.contrib.admin',

    'wise.worksheet',
    # Gunicorn needs to be installed in site-packages or dropped
    # into the same directory as this file, if you can't run
    # ' import gunicorn ' form this directory then it will fail
    'reversion',
    'piston',
#    'debug_toolbar',
)

# Sphinx sometimes complains about paths if it is run from a
# different directory so this flag disables all the template
# precaching / path loading so that Sphinx can complete. If this
# is enabled then the worksheet will *NOT* work.
IGNORE_PATHS = False

# JIT compile *all* Pure libraries on boot. This ensures there
# aren't any hiccups when executing Pure functions initially.
# This is experimental and is also quite slow and breaks
# more often then not.
PRECOMPILE  = True
