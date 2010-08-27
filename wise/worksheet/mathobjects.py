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


#-------------------------------------------------------------
# Rule Cache
#-------------------------------------------------------------

rulecache = {}

#for rule in Rule.objects.all():
#    rule = rule.pure
#    hsh = hash(rule)
#
#    if hsh in rulecache:
#        plevel = rulecache[hsh]
#    else:
#        plevel = pure.PureLevel([rule])
#        rulecache[hsh] = plevel
#        #print 'Building Pure rule: ( %s , %s )' % (hsh, rule)
#
#    #print 'Rule cache size:', len(rulecache)

#-------------------------------------------------------------
# Base Term Class 
#-------------------------------------------------------------

# Philosophy for Math Objects
#
# Objects should only be inherited if they follow the Liskov
# Substitution Principle i.e. 
#
#    Let q(x) be a property provable about objects x of type T.
#    Then q(y) should be true for objects y of type S where S is
#    a subtype of T.

from base.objects import *

#-------------------------------------------------------------
# Transforms
#-------------------------------------------------------------

#import algebra

#print [i.domain for i in algebra.mappings]

#generate_translation(root=Term)
#generate_translation(root=Equation)
#generate_pure_objects(root=Term)
#generate_pure_objects(root=Equation)

