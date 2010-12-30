# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.


from wise.worksheet.utils import *

from wise.utils.bidict import bidict
from wise.utils.patterns import TranslationTable

import meta_inspector
from django.conf import settings

import wise.worksheet.exceptions as exception
from wise.utils.module_loading import module_has_submodule
from django.utils.importlib import import_module

def all_subclasses(cls, accumulator=set(),
                        depth=1, 
                        max_inheritance_depth=30):

    accumulator.update(cls.__subclasses__())

    if depth < max_inheritance_depth:
        for scls in cls.__subclasses__():
            all_subclasses(scls, accumulator, depth=depth+1)

    return accumulator

# bidict can hash the following types: 'type', 'class', 'int', 'str'

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

python_trans = PythonTranslationTable()
pure_trans   = PureTranslationTable()

pyobjects = python_trans
translation_table = pure_trans

def translate_pure(key):
    try:
        return pure_trans[key]
    except KeyError:
        raise exception.NoWrapper(key)

def build_translation(pure=False):
    for name, package in meta_inspector.PACKAGES.iteritems():
        pack_module = import_module(name)

        if module_has_submodule(pack_module, 'objects'):
            print 'Importing objects from ... ' + name
            path = name + '.objects'
            pack_objects = import_module(path, settings.ROOT_MODULE)

            super_clss, nullary_types = pack_objects.initialize()
            pure_trans.populate(nullary_types)

            package = meta_inspector.Package(name=name)

            # Use sets, so we can do interesections to check for
            # namespace collisions later
            provided_symbols = set(super_clss)
            _pure_trans = {}

            # Grab all the sbuclasses for the top superclasses
            # and join to the objects store
            for cls in super_clss:
                provided_symbols.update(all_subclasses(cls))

            for cls in provided_symbols:
                package.provided_symbols[cls.__name__] = cls

                if cls.pure:
                    _pure_trans[cls.pure] = cls

            python_trans.populate(package.provided_symbols)
            pure_trans.populate(_pure_trans)

            meta_inspector.PACKAGES[name] = package
            meta_inspector.PACKAGES.sync()

def build_python_lookup(force=False):
    if not python_trans.loaded or force:
        build_translation()
    return python_trans

def build_pure_lookup(force=False):
    if not pure_trans.loaded or force:
        build_translation()
    return pure_trans

def build_all_lookup(force=False):
    if not pure_trans.loaded or not python_trans.loaded or force:
        build_translation()
    return python_trans, pure_trans

def build_cython_objects(force=False, jit=False):
    from wise.translators.pure_wrap import generate_pure_object, jit_compile_interp

    for obj in pure_trans.table._fwd.itervalues():
        generate_pure_object(obj)
        print obj, (obj.po == None) or 'Success'

    if settings.PRECOMPILE or jit:
        jit_compile_interp()

def get_python_lookup():
    return python_trans

def get_pure_lookup():
    return pure_trans
