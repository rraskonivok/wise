# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.


from wise.worksheet.utils import *
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
pyobjects = TranslationTable()

translation_table = {}

def generate_translation(root, package, pure=False):
    # Do want to prebuild Pure ( Cython ) objects
    if pure:
        generate_pure_objects(root=root)
        if root.pure:
            translation_table[root.pure] = root

    pyobjects[root.__name__] = root
    package.provided_symbols[root.__name__] = root

    for cls in root.__subclasses__():
        if cls.pure:
            if not cls.pure in translation_table:
                pyobjects[cls.__name__] = cls
                package.provided_symbols[cls.__name__] = cls
                translation_table[cls.pure] = cls

        generate_translation(cls, package, pure)

def translate_pure(key):
    try:
        return translation_table[key]
    except KeyError:
        raise exception.NoWrapper(key)

def build_translation(pure=False):
    if pure:
        from wise.translators.pure_wrap import generate_pure_objects

    for name, package in meta_inspector.PACKAGES.iteritems():
        pack_module = import_module(name)

        if module_has_submodule(pack_module, 'objects'):
            print 'Importing objects from ... ' + name
            path = name + '.objects'
            pack_objects = import_module(path, settings.ROOT_MODULE)

            super_clss, nullary_types = pack_objects.initialize()
            translation_table.update(nullary_types)

            package = meta_inspector.Package(name=name)

            # Use sets, so we can do interesections to check for
            # namespace collisions later
            provided_symbols = set(super_clss)

            # Grab all the sbuclasses for the top superclasses
            # and join to the objects store
            for cls in super_clss:
                provided_symbols.update(all_subclasses(cls))

            for cls in provided_symbols:
                package.provided_symbols[cls.__name__] = cls

                if cls.pure:
                    translation_table[cls.pure] = cls

            #pyobjects.populate(provided_symbols)

            from pprint import pprint
            pprint(provided_symbols)

            #generate_translation(cls, package, pure)

            meta_inspector.PACKAGES[name] = package
            meta_inspector.PACKAGES.sync()

def build_python_lookup():
    pass

build_translation()

