# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import token

import sys, os, re
from re import VERBOSE

from funcparserlib import util
from funcparserlib.lexer import make_tokenizer, Spec
from funcparserlib.parser import (maybe, many, finished, skip, forward_decl,
    SyntaxError, with_forward_decls, oneplus)
from funcparserlib.contrib.common import const, n, op, op_, sometok

def tokenize(str):
    'str -> Sequence(Token)'
    specs = [
        Spec('space', r'[ \t\r\n]+'),
        Spec('number', r'''
            -?                  # Minus
            (0|([1-9][0-9]*))   # Int
            (\.[0-9]+)?         # Frac
            ([Ee][+-][0-9]+)?   # Exp
            ''', VERBOSE),
        Spec('op', r'[()\[\]\-,:]'),
        Spec('name', r'[A-Za-z_][A-Za-z]*'),
    ]
    useless = ['space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in useless]

def pure_parse(seq):
    'Sequence(Token) -> object'

    #http://pure-lang.googlecode.com/svn/docs/pure-syntax/pure-syntax.pdf&pli=1

    def make_number(n):
        try:
            return int(n)
        except ValueError:
            return float(n)

    def make_name(s):
        return s

    number = sometok('number') >> make_number
    var = sometok('name') >> make_name

    atom = var | number | ( op_('(') + number + op_(')') )

    @with_forward_decls
    def sexp():
        return op_('(') + atom + many(atom|sexp) + op_(')')

    @with_forward_decls
    def funcapp():
        return var + many(atom|sexp)

    @with_forward_decls
    def pure():
        return ( atom + skip(finished) ) | funcapp

    primary = pure

    return primary.parse(tokenize(seq))

def sexp_parse(seq):
    'Sequence(Token) -> object'

    def make_number(n):
        try:
            return int(n)
        except ValueError:
            return float(n)

    def make_name(s):
        return s

    number = sometok('number') >> make_number
    var = sometok('name') >> make_name

    atom = var | number

    @with_forward_decls
    def sexp():
        return op_('(') + atom + many(atom|sexp) + op_(')')

    @with_forward_decls
    def funcapp():
        return var + many(atom|sexp)

    primary = sexp

    return primary.parse(tokenize(seq))
