#!/usr/bin/env ipython
import sys
import os
from string import strip

from optparse import OptionParser
import settings
from utils.patterns import Aggregator
import ConfigParser

PACKAGES = Aggregator(file='packages_cache')

class Package(object):
    name = 'unknown'
    author = 'unknown'
    version = 'unknown'
    path = 'unknown'
    date = 'unknown'
    cached_date = 'unknown'
    depends = []
    files = []

    provided_rules = []
    provided_transforms = []
    provided_panels = []
    translation_table = []

    def __init__(self, **kwargs):
        self.provided_symbols = {}
        self.__dict__.update(kwargs)

    def provides(self, symbol):
        self.provided_symbols.append(symbol)

def str2list(s):
    return map(strip,s.split(','))

def rebuild_modules(packages):
    print 'Rebuilding package database.'

    for package in packages:
        kwargs = {}
        kwargs['name'] = package
        try:
            config = ConfigParser.ConfigParser()
            config.read(os.path.join(package, 'files'))
            files = str2list(config.get('files','pure'))
            kwargs['files'] = files

            config = ConfigParser.ConfigParser()
            config.read(os.path.join(package, 'depends'))
            depends = str2list(config.get('depends','depends'))
            kwargs['depends'] = depends

            config = ConfigParser.ConfigParser()
            config.read(os.path.join(package, 'desc'))

            # Find all keys in the desc section
            for option in config.items('desc'):
                key, val = option
                kwargs[key] = val

            print kwargs
            PACKAGES[package] = Package(**kwargs)

        except:
            print 'Invalid Config for Package:', package
            raise

        PACKAGES.sync()
        print PACKAGES['base'].__dict__

    #for installed in settings.INSTALLED_MATH_PACKAGES:
    #    PACKAGES[installed] = Package(name=installed)

# Upon initial import of this module check to see if we have a
# package cache, if not then build it
if len(PACKAGES) == 0:
    print 'Package database is blank. Run wpm --rebuild'
