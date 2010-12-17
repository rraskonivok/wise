from django.conf import settings
from utils.aggregator import Aggregator

PACKAGES = Aggregator(file='packages_cache')

class Package(object):
    name = 'unknown'
    author = 'unknown'
    version = 'unknown'
    path = 'unknown'
    date = 'unknown'
    cached_date = 'unknown'

    module_string = None

    provided_symbols = {}
    provided_rules = []
    provided_transforms = []
    provided_panels = []
    translation_table = []

    def __init__(self, **kwargs):
        self.name = kwargs['name']

    def provides(self, symbol):
        self.provided_symbols.append(symbol)

def rebuild_modules():
    for installed in settings.INSTALLED_MATH_PACKAGES:
        print 'creating', installed
        PACKAGES[installed] = Package(name=installed)

# Upon initial import of this module check to see if we have a
# package cache, if not then build it
if len(PACKAGES) == 0:
    rebuild_modules()
else:
    if settings.DEBUG:
        for name, package in PACKAGES.iteritems():
            print package.provided_symbols
        print 'Using cached Package directory.'
