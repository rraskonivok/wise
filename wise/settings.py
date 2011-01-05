# If you are using gevent workers with gunicorn then unhighlight
# the next two lines:
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

# Debug=True then static files will be served by Django/Gunicorn
DEBUG = True

MANAGERS = ADMINS

# Set your database information here. If left as is then it will
# create a sqlite database which should work with no
# configuration.
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

# The root module for wise
ROOT_MODULE = 'wise'
# Module contianing packages
PACK_MODULE = ROOT_MODULE + '.packages'

# `base` is the minimum needed to run
INSTALLED_MATH_PACKAGES = ('base',)

#---------------------------
# Message Queues
#---------------------------

WORKER_TYPE = 'sync' # celery-redis, celery-rabbitmq

# Note:
# Celery is installed by default, BUT if you set
# WORKER_TYPE=sync then you do not need to set up a message queue
# or broker. All tasks will execute in the Django main event loop
# additional configuration is needed.

# Set one of these up if you so desire. RabbitMQ is faster, Redis
# is simpler.

# Redis
# =====
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


# RabbitMQ
# ========
#BROKER_HOST = "localhost"
#BROKER_PORT = 5672
#BROKER_USER = "user"
#BROKER_PASSWORD = "pass"
#BROKER_VHOST = "myvhost"
#CELERY_RESULT_BACKEND = "amqp"

#CELERY_DISABLE_RATE_LIMITS=True
#CELERY_DB_REUSE_MAX=100
CELERY_ALWAYS_EAGER = WORKER_TYPE == 'sync'

#---------------------------
# Caches
#---------------------------

# Change to your desired cache or disable. If you use a database
# then Initially you may need to run: manage.py createcachetable
#CACHE_BACKEND = 'db://cache'

#---------------------------
# Django Enviroment
#---------------------------

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_ETAGS = False

# In order to use the Django admin interface with gunicorn you'll
# need to grab the admin resources from your local install. Use
# the script static/copy_admin_resources.sh to do this. This
# script will build /static/admin
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Change this to something special and don't share it with
# anyone, Django uses this to salt password hashes
SECRET_KEY = 'changeme'

# If DEBUG = True, then only addresses in INTERNAL_IPS will be
# able to access the admin interface
INTERNAL_IPS = ('127.0.0.1',)

# Globally block an IP address
BLOCKED_IPS = []

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    'django.core.context_processors.static',
#    "django.contrib.messages.context_processors.messages",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.XHTMLMiddleware',
    'middleware.BlockedIpMiddleware',
#    'privatebeta.middleware.PrivateBetaMiddleware',
#    'middleware.ErrorMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

#---------------------------
# Static Media
#---------------------------

APPEND_SLASH = True
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')

# MEDIA_URL is what media_bundler prefixes it's path with when it
# compiles bundles of static files ( see worksheet/media.py )
if DEBUG == True:
    # In development mode serve static content out of static
    # using django.contrib.staticfiles
    MEDIA_URL = '/static/'
    STATIC_ROOT = "static/"
    STATIC_URL = '/static/'

elif DEBUG == False:
    # In production mode serve static content out of static
    # using nginx. Use manage.py collectstatic to aggregate
    MEDIA_URL = '/'
    STATIC_ROOT = "media/"
    STATIC_URL = '/'

STATICFILES_DIRS = (
    MEDIA_ROOT,
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
TEMPLATE_DEBUG = DEBUG
USE_BUNDLES = False
DEFER_JAVASCRIPT = False

from worksheet.media import MEDIA_BUNDLES

#---------------------------
# Apps
#---------------------------

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'wise.worksheet',
    'gunicorn',
    'djcelery',
    # In order to use admin with gunicorn you'll need to grab the
    # admin resources from your local install. Use the script
    # static/copy_admin_resources.sh to do this. Or you can
    # install the grapelli admin interface with:
    # `pip install -E wise grappelli`
    'piston',
    #'privatebeta',
    'media_bundler',
    'registration',
    # Optional Applications - mostly for development
    #'debug_toolbar',
    #'django_extensions',
]

#---------------------------
# Optional Apps
#---------------------------

# django-sentry - Real-time logging
try:
    import indexer, paging, sentry, sentry.client
    INSTALLED_APPS  += ['indexer', 'paging', 'sentry', 'sentry.client']
except ImportError:
    pass

# Grapelli - prettier admin interface
try:
    import grappelli
    INSTALLED_APPS += ['grappelli','django.contrib.admin']
except:
    INSTALLED_APPS += ['django.contrib.admin']

#---------------------------
# Debug Options
#---------------------------

# Disable Pure from staring entirely
DISABLE_PURE = False

# Don't use `shelve` to cache lookup tables, rebuild them
# on every boot. Can be quite slow.
NOCACHE = False


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
