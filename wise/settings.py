#try:
#    from gevent import monkey; monkey.patch_all()
#except:
#    pass

import os
import djcelery
djcelery.setup_loader()

# A quick note about security. **WISE IS ALPHA SOFTWARE AND NOT
# SECURE** (yet)
ADMINS = (
    # ('Leonhard Euler', 'leuler@unibas.ch'),
)

MANAGERS = ADMINS

# Set your database information here

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wise.db',  # Or path to database file if using sqlite3.
        'USER': '',         # Not used with sqlite3.
        'PASSWORD': '',     # Not used with sqlite3.
        'HOST': '',         # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',         # Set to empty string for default. Not used with sqlite3.
    }
}

# `base` is the minimum needed to run
INSTALLED_MATH_PACKAGES = ('base',)

WORKER_TYPE = 'celery' # celery-redis, celery-rabbitmq

# -----------------------
# Redis
# -----------------------

# Use redis as a queue
#BROKER_BACKEND = "kombu.transport.pyredis.Transport"
#BROKER_HOST = "localhost"
#BROKER_PORT = 6379
#BROKER_VHOST = "0"

# Store results in redis
#CELERY_RESULT_BACKEND = "redis"
#REDIS_HOST = "localhost"
#REDIS_PORT = 6379
#REDIS_DB = "0"

# -----------------------
# RabbitMQ
# -----------------------
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "test"
BROKER_PASSWORD = "test"
BROKER_VHOST = "myvhost"
CELERY_RESULT_BACKEND = "amqp"

CELERY_DISABLE_RATE_LIMITS=True
CELERY_DB_REUSE_MAX=100
CELERY_ALWAYS_EAGER = WORKER_TYPE == 'sync'

# Change to your desired cache or disable. Initially you may need
# to run
#
#    python manage.py createcachetable
#
#CACHE_BACKEND = 'db://cache'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False
USE_L10N = False
USE_ETAGS = False

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_URL = '/static/'

APPEND_SLASH = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DISABLE_PURE = False

# In order to use the Django admin interface with gunicorn you'll
# need to grab the admin resources from your local install. Use
# the script static/copy_admin_resources.sh to do this. This
# script will build /static/admin
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Change this to something special, Django uses this to salt
# password hashes
SECRET_KEY = 'changeme'

INTERNAL_IPS = ('127.0.0.1',)
BLOCKED_IPS = []

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.XHTMLMiddleware',
#    'middleware.ErrorMiddleware',
    'middleware.BlockedIpMiddleware',
    'privatebeta.middleware.PrivateBetaMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

from worksheet.media import MEDIA_BUNDLES
MEDIA_GENERATORS = (
    'mediagenerator.generators.copyfiles.CopyFiles',
    'mediagenerator.generators.bundles.Bundles',
    'mediagenerator.generators.manifest.Manifest',
)

ROOT_URLCONF = 'wise.urls'
ROOTDIR = os.path.abspath(os.path.dirname(__file__))

# Template directories include:
# templates/
# worksheet/templates
# $PACKAGES/templates
TEMPLATE_DIRS = tuple(
    [ROOTDIR +'/templates'] +
    [ROOTDIR + ('/%s/templates' % pack) for pack in INSTALLED_MATH_PACKAGES]
)

USE_BUNDLES = False
DEFER_JAVASCRIPT = False

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'wise.worksheet',
    'gunicorn',
    'djcelery',
    # In order to use admin with gunicorn you'll need to grab the
    # admin resources from your local install. Use the script
    # static/copy_admin_resources.sh to do this. Or you can
    # install the grapelli admin interface with:
    # `pip install -E wise grappelli`
    'piston',
    'privatebeta',
    'media_bundler',
    'registration',
    # Optional Applications - mostly for development
    #'debug_toolbar',
    #'django_extensions',
]

# Check if we have any optional apps

# Logging with django-sentry
try:
    import indexer, paging, sentry, sentry.client
    INSTALLED_APPS  += ['indexer', 'paging', 'sentry', 'sentry.client']
except ImportError:
    pass

# Prettier admin interface
try:
    import grappelli
    INSTALLED_APPS += ['grappelli','django.contrib.admin']
except ImportError:
    INSTALLED_APPS += ['django.contrib.admin']

# Version control on Models
try:
    INSTALLED_APPS += ['reversion']
except ImportError:
    pass


# In case somebody wants to fork under a new name
ROOT_MODULE = 'wise'

# Some browsers require the Content-Type to be
# `application/xhtml+xml` in order to render mixed doctype HTML +
# MathML
FORCE_XHTML = False

# Sphinx sometimes complains about paths if it is run from a
# different directory so this flag disables all the template
# precaching / path loading so that Sphinx can complete. If this
# is enabled then the worksheet will *NOT* work.
IGNORE_PATHS = False

# JIT compile *all* Pure libraries on boot. This ensures there
# aren't any hiccups when executing Pure functions initially.
# This is experimental and is also quite slow and breaks
# more often then not.
PRECOMPILE = False
