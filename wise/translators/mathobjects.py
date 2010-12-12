# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.conf import settings

from wise.worksheet.utils import *
import wise.worksheet.exceptions as exception

from wise.translators.pure_wrap import generate_pure_objects

#-------------------------------------------------------------
# Pure Wrapper
#-------------------------------------------------------------

ROOT_MODULE = 'wise'

translation_table = {}
pyobjects = {}

def generate_translation(root):
    generate_pure_objects(root=root)
    if root.pure:
        translation_table[root.pure] = root

    pyobjects[root.__name__] = root

    for cls in root.__subclasses__():
        if cls.pure:
            if not cls.pure in translation_table:
                pyobjects[cls.__name__] = cls
                translation_table[cls.pure] = cls
        generate_translation(cls)

def translate_pure(key):
    try:
        return translation_table[key]
    except KeyError:
        raise exception.NoWrapper(key)

def build_translation():
    for pack in settings.INSTALLED_MATH_PACKAGES:
        #path = '.'.join([ROOT_MODULE,pack,'objects'])
        #mod = __import__(str(path),globals(),locals())
        #for k in dir(mod):
        #    print mod.__dict__[k]
        #    globals()[k] = mod.__dict__[k]

        # I give up
        exec('from %s.%s.objects import initialize' % (ROOT_MODULE,pack))
        mod_top, mod_table = initialize()
        translation_table.update(mod_table)

        for cls in mod_top:
            generate_translation(root=cls)

build_translation()

#import worksheet.uml as uml
#uml.generate(Term)
