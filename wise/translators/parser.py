# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
from re import VERBOSE

from funcparserlib.contrib.common import op_, op, sometok
from funcparserlib.lexer import make_tokenizer, Spec
from funcparserlib.parser import (many, maybe, finished, skip,
with_forward_decls, forward_decl, oneplus)

# The same tokens are used for both Sexp and Pure parsers
def tokenize(str):
    'str -> Sequence(Token)'
    specs = [
        Spec('space', r'[ \t\r\n]+'),
        Spec('number', r'''
            -?                  # Minus
            (0|([1-9][0-9]*))   # Int
            (\.[0-9]+)?         # Frac
            ([Ee][+-][0-9]+)?   # Exp
            (L)?                # Long
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

    # This is some beautiful code... whatever it's fast
    def make_number(n):
        if 'L' in n:
            return long(n)

        try:
            return int(n)
        except ValueError:
            return float(n)

    def make_array(n):
        if n is None:
            return []
        else:
            return [n[0]] + n[1]

    def make_name(s):
        return s

    number = sometok('number') >> make_number
    var = sometok('name') >> make_name
    atom = var | number | ( op_('(') + number + op_(')') )
    first_order = forward_decl()

    #@with_forward_decls

    @with_forward_decls
    def expr():
        return op_('(') + var + oneplus(expr|funcapp|atom) + op_(')')

    @with_forward_decls
    def funcapp():
        return (
            var + many(expr|atom)
        )

    @with_forward_decls
    def array():
        return (op_('[') +
            maybe((funcapp|atom) + oneplus(op_(',') + first_order)) +
            op_(']')
            >> make_array)

    # First order objects
    first_order.define(
        funcapp |
        #array |
        atom
    )

    @with_forward_decls
    def pure():
        return ( first_order + skip(finished) ) | first_order

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

def pretty_print_sexp(parsed):
    from pprint import pprint
    pprint(parsed)
