# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from types import ClassType, TypeType

from django.conf import settings
from django.utils.importlib import import_module

import wise.meta_inspector
import wise.worksheet.exceptions as exception

from wise.worksheet.utils import *
from wise.packages.loader import load_package_module, load_package
from wise.translators.pure_wrap import PureInterface, PublicRule
from wise.translators import pureobjects
from wise.utils.bidict import bidict
from wise.utils.patterns import TranslationTable, Aggregator
from wise.utils.module_loading import module_has_submodule


def all_subclasses(cls, accumulator=None,
                        depth=1,
                        max_inheritance_depth=30):

    if not accumulator:
        accumulator = set([])

    accumulator.update(cls.__subclasses__())

    if depth < max_inheritance_depth:
        for scls in cls.__subclasses__():
            all_subclasses(scls, accumulator=accumulator, depth=depth+1)

    return accumulator

def collect_objects(package, recursive=False):
    """
    Run through `$PACKAGE.objects` and collect all objects which
    are subclasses of the superclasses provided in the
    `$PACKAGE.objects.initialize` function.
    """
    pack_objects = load_package_module(package,'objects')
    super_clss, nullary_types = pack_objects.initialize()

    classes = {}
    inherited = {}

    for clsname, cls in pack_objects.__dict__.iteritems():
        if type(cls) is TypeType and issubclass(cls,tuple(super_clss)):
            classes[cls.__name__] = cls

    if recursive:
        for cls in classes.itervalues():
            for scls in all_subclasses(cls):
                inherited[scls.__name__] =  scls

    if recursive:
        return classes, inherited
    else:
        return classes

#-------------------------------------------------------------
# Python Math Translation
#-------------------------------------------------------------

# Maps str -> Python classes, as defeind PACKAGE/objects.py

# Example:
# {
#   'Numeric': <class 'base.objects.Numeric'>,
#   'Addition': <class 'base.objects.Addition'>,
# }

class PythonTranslationTable(TranslationTable):

    __shared_state = dict(
        table = bidict(),

        loaded = False,
        locked = False,
    )

    def __init__(self, new=False):
        self.__dict__ = self.__shared_state

class PureTranslationTable(TranslationTable):

    __shared_state = dict(
        table = bidict(),

        loaded = False,
        locked = False,
    )

    def __init__(self, new=False):
        self.__dict__ = self.__shared_state

#---------------------------
# Rule Translation
#---------------------------

#TODO: remove this
def translate_pure(key):
    try:
        return pure_trans[key]
    except KeyError:
        raise exception.NoWrapper(key)

def build_python_lookup(force=False):
    if python_trans.loaded and not force:
        return

    for name in settings.INSTALLED_MATH_PACKAGES:
        pack_module = load_package(name)
        package = wise.meta_inspector.PACKAGES[name]

        if module_has_submodule(pack_module, 'objects'):
            print 'Building Python translation table from ... ' + name

            pack_objects = load_package_module(name,'objects')
            super_clss, nullary_types = pack_objects.initialize()

            first_order_symbols, all_symbols = collect_objects(name, recursive=True)
            python_trans.populate(first_order_symbols)
            python_trans.populate(all_symbols)

            # Give the package a list of strings containing the
            # classnames of the provided symbols and update the
            # persistence in memory value and sync to the disk
            if not package.provided_symbols:
                wise.meta_inspector.PACKAGES.make_writable()

                for sym in first_order_symbols.iterkeys():
                    package.provides(sym)

                wise.meta_inspector.PACKAGES[name] = package
                wise.meta_inspector.PACKAGES.sync()
            else:
                if settings.DEBUG:
                    pass
                    #print 'Not rebuilding symbol table for:', name

    return python_trans


def build_pure_lookup(force=False):
    if pure_trans.loaded and not force:
        return

    for name in settings.INSTALLED_MATH_PACKAGES:
        pack_module = load_package(name)
        package = wise.meta_inspector.PACKAGES[name]

        if module_has_submodule(pack_module, 'objects'):
            print 'Building Pure translation table from ... ' + name

            pack_objects = load_package_module(name,'objects')
            super_clss, nullary_types = pack_objects.initialize()

            # Populate the Pure translation table with nullary
            # objects
            pure_trans.populate(nullary_types)

    _pure_trans = {}
    for cls in python_trans.table.values():
        if hasattr(cls,'pure'):
            _pure_trans[cls.pure] = cls

    pure_trans.populate(_pure_trans)

    return pure_trans

def build_rule_lookup(force=False):
    """
    Build translation table for all available rules from
    PACKAGES/rules.py
    """

    if rulesets and not settings.NOCACHE:
        print 'Using cached rulesets file.'
        BUILD_RULESETS = False
    else:
        BUILD_RULESETS = True

    if rules and not settings.NOCACHE:
        print 'Using cached rules file.'
        BUILD_RULES = False
    else:
        BUILD_RULES = True

    if not (BUILD_RULESETS and BUILD_RULES):
        return

    for name in settings.INSTALLED_MATH_PACKAGES:
        pack_module = import_module('packages.' + name)

        # Load PACKAGE/rules.py
        if module_has_submodule(pack_module, 'rules'):
            print 'Importing rules from ... ' + name

            path = name + '.rules'
            pack_objects = import_module('packages.' + path, settings.ROOT_MODULE)

            # Build mathobjects.rulesets:
            # ------------------------
            # get PACKAGE.rules.panel ( a dictionary object )
            # which contains the hierarchy of rules to use in the
            # worksheet panels. Looks something like:
            # {'Commutative Algebra': ['algebra_normal
            if BUILD_RULESETS:
                rulesets.make_writable()
                rulesets.update(pack_objects.panel)
                rulesets.sync()

            # Build mathobjects.rules:
            # ------------------------
            # Scrape all classes of type `PublicRule` from teh
            # module and load into the
            if BUILD_RULES:
                rules.make_writable()
                for name, symbol in pack_objects.__dict__.iteritems():
                    if type(symbol) is ClassType and issubclass(symbol, PublicRule):
                        rules[name] = symbol
                        #print name

                        # Register the rule in the translation dictionary
                        if hasattr(symbol,'register'):
                            symbol.register(a)
                rules.sync()

def build_cython_objects(force=False, jit=False):
    interface = PureInterface()

    if len(cy_objects) > 0 and not force:
        return

    for pack in settings.INSTALLED_MATH_PACKAGES:
        # Query meta_inspector to find the packages path
        path = wise.meta_inspector.PACKAGES[pack].path

        # Convert the Unix path to a Pure style path
        pure_path = '::'.join(path.split('/'))

        interface.use(pure_path,pack)

    print 'Building Cython Objects'

    for obj in pure_trans.table._fwd.itervalues():
        if obj.pure:
            if obj.pure not in cy_objects:
                #print obj.pure
                obj.po = pureobjects.PureSymbol(obj.pure)
                cy_objects.add(obj.pure)
            else:
                raise Exception('Namespace collision: ' + obj.pure)
        #print obj, (obj.po == None) or 'Success'

    if settings.PRECOMPILE or jit:
        interesections.jit_compile()

def is_mapping(obj):
   return hasattr(obj,'mapping')

def build_transform_lookup(force=False):
    """
    Build translation table for all available transforms from
    PACKAGES/transforms.py
    """
    if transforms and not settings.NOCACHE:
        print 'Using cached transforms file.'
        return

    for pack_name in settings.INSTALLED_MATH_PACKAGES:
        print 'Importing transforms from ... ' + pack_name
        pack_module = import_module('packages.' + pack_name)

        # Load PACKAGE/rules.py
        if module_has_submodule(pack_module, 'transforms'):
            path = pack_name + '.transforms'
            pack_transforms = import_module('packages.' + path, settings.ROOT_MODULE)

            transforms.make_writable()
            for name, symbol in pack_transforms.__dict__.iteritems():
                if is_mapping(symbol):
                    symbol.package = pack_name
                    transforms[name] = symbol

            transforms.sync()

def get_python_lookup():
    return python_trans

def get_pure_lookup():
    return pure_trans

# ----------------------------------------
# Translation tables
# ----------------------------------------

transforms = Aggregator(file = 'cache/transforms_cache')
rules      = Aggregator(file = 'cache/rules_cache')
rulesets   = Aggregator(file = 'cache/rulesets_cache')
cy_objects = set()

# These are all singletons, so they can be passed around
python_trans = PythonTranslationTable()
pure_trans   = PureTranslationTable()

# For compatability
translation_table = pure_trans
