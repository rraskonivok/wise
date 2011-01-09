#!/usr/bin/env ipython
import os
from string import strip

import settings
from utils.patterns import Aggregator
import ConfigParser

PACKAGES = Aggregator(file='cache/packages_cache')
blacklist = set(['pkgtemplate'])
required_files = ['desc', 'files', 'depends']
PACKAGE_DIR = settings.PACKAGE_DIR

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

def is_package(top):
    return all(f in os.listdir(os.path.join(PACKAGE_DIR,top)) for f in required_files)

def lsdirs(top):
    return (path for path in os.listdir(top) if
            os.path.isdir(os.path.join(top,path)))

def lspackages():
    return set([d for d in lsdirs(PACKAGE_DIR) if is_package(d)]) - blacklist

def rebuild_modules(packages):
    print 'Rebuilding package database.'
    PACKAGES.make_writable()

    for package in packages:
        pack_path = os.path.join(PACKAGE_DIR,package)
        kwargs = {}
        kwargs['name'] = package
        try:
            config = ConfigParser.ConfigParser()
            config.read(os.path.join(pack_path, 'files'))
            files = str2list(config.get('files','pure'))
            kwargs['files'] = files

            config = ConfigParser.ConfigParser()
            config.read(os.path.join(pack_path, 'depends'))
            depends = str2list(config.get('depends','depends'))
            kwargs['depends'] = depends

            config = ConfigParser.ConfigParser()
            config.read(os.path.join(pack_path, 'desc'))

            # Find all keys in the desc section
            for option in config.items('desc'):
                key, val = option
                kwargs[key] = val

            kwargs['path'] = pack_path
            PACKAGES[package] = Package(**kwargs)

        except:
            print 'Invalid metadata for package:', package
            raise

    PACKAGES.sync()

# Upon initial import of this module check to see if we have a
# package cache, if not then build it
if len(PACKAGES) == 0:
    rebuild_modules(lspackages())
    print 'Package database is blank. Rebuilding'
