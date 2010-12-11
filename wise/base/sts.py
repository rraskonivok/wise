# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from wise.base.cell import Cell
from wise.base.term import Term

from wise.base.toplevel import Equation, Definition, Function

from math import modf

from wise.worksheet.utils import render_haml_to_response

import worksheet.exceptions as exception

from utils.latex import greek_lookup
from worksheet.utils import *

from django import template

def Type(object):

    base = None
    spec = None

    def __init__(self):
        pass

def Morphism(object):
    '''
    This symbol represents the construction of a function type.

    The first n-1 children denote the types of the arguments,
    the last denotes the return type.
    '''

    codomain = None
    domain = None

    def __init__(self):
        pass

def Nary(object):

    def __init__(self):
        pass

def Nassoc(object):

    def __init__(self):
        pass

def Structure(object):

    def __init__(self):
        pass
