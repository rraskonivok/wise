#!/usr/bin/env python
import sys

from optparse import OptionParser
import settings
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
        PACKAGES[installed] = Package(name=installed)

# Upon initial import of this module check to see if we have a
# package cache, if not then build it
if len(PACKAGES) == 0:
    rebuild_modules()
else:
    if settings.DEBUG:
        #for name, package in PACKAGES.iteritems():
        #    print package.provided_symbols
        print 'Using cached Package directory.'

def main():
    parser = OptionParser()
    parser.add_option("-p",
                      "--packages",
                      dest="packages",
                      action="store_true",
                      help="Return installed Pure libraries to stdout")

    parser.add_option("-s",
                      "--shell",
                      dest="packages",
                      action="store_true",
                      help="Pure shell with installed libraries")

    (options, args) = parser.parse_args()

    if options.packages:
        libraries = settings.INSTALLED_MATH_PACKAGES
        line = ['%s/%s.pure' % (lib,lib) for lib in libraries]
        line += ['pure/prelude.pure']
        sys.stdout.write('pure -i -q ' + ' '.join(line) + "\n")

if __name__ == "__main__":
   main()
