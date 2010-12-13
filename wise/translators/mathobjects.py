# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from meta_inspector import Package
import meta_inspector

from django.conf import settings

from wise.worksheet.utils import *
import wise.worksheet.exceptions as exception

import wise.worksheet.exceptions as exception
from wise.translators.pure_wrap import generate_pure_objects

#-------------------------------------------------------------
# Pure Wrapper
#-------------------------------------------------------------

translation_table = {}
pyobjects = {}

def generate_translation(root, package):

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

        generate_translation(cls, package)

def translate_pure(key):
    try:
        return translation_table[key]
    except KeyError:
        raise exception.NoWrapper(key)

def build_translation():
    for name, package in meta_inspector.PACKAGES.iteritems():
        exec('from %s.%s.objects import initialize' % (settings.ROOT_MODULE, name))
        mod_top, mod_table = initialize()
        translation_table.update(mod_table)

        package = Package(name=name)

        for toplevel in mod_top:
            generate_translation(toplevel, package)

        meta_inspector.PACKAGES[name] = package
        meta_inspector.PACKAGES.sync()

build_translation()
