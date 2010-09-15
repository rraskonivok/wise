# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from wise.worksheet.utils import *
from wise.worksheet.models import Symbol, Function, Rule
import wise.worksheet.exceptions as exception

from pure_wrap import generate_pure_objects

#-------------------------------------------------------------
# Pure Wrapper
#-------------------------------------------------------------

translation_table = {}

def generate_translation(root):
    if root.pure:
        #print 'Building Python translation pair: ( %s , %s )' % (root.pure, root)
        translation_table[root.pure] = root

    for cls in root.__subclasses__():
        if cls.pure:
            if not cls.pure in translation_table:
                translation_table[cls.pure] = cls
        generate_translation(cls)

active_objects = {}

def translate_pure(key):
    try:
        return translation_table[key]
    except KeyError:
        raise exception.NoWrapper(key)


from wise.base.objects import *
from wise.logic.objects import *

#-------------------------------------------------------------
# Transforms
#-------------------------------------------------------------

generate_translation(root=Term)
generate_translation(root=Equation)
generate_pure_objects(root=Term)
generate_pure_objects(root=Equation)

#import uml
#uml.generate(Term)
