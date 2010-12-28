# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import token

# Special thanks to fellow Arch Linux user Andrey Vlasovskikh for
# writing this genius library, it scales wonderfully and has been
# the one fixed point in my code for 6 months of development.
from funcparserlib.parser import some, a, many, skip, finished, \
maybe, forward_decl, with_forward_decls, oneplus

from tokenize import generate_tokens
from StringIO import StringIO

class Token(object):
    def __init__(self, code, value, start=(0, 0), stop=(0, 0), line=''):
        self.code = code
        self.value = value
        self.start = start
        self.stop = stop
        self.line = line

    @property
    def type(self):
        return token.tok_name[self.code]

    def __unicode__(self):
        pos = '-'.join('%d,%d' % x for x in [self.start, self.stop])
        return "%s %s '%s'" % (pos, self.type, self.value)

    def __repr__(self):
        return 'Token(code: %r, value: %r, start: %r, stop: %r, line:%r)\n' % (
            self.code, self.value, self.start, self.stop, self.line)

    def __eq__(self, other):
        return (self.code, self.value) == (other.code, other.value)

def tokenize(s):
    'str -> [Token]'
    return list(Token(*t)
        for t in generate_tokens(StringIO(s).readline)
        if t[0] not in [token.NEWLINE])

def tokval(tok):
    'Token -> str'
    return tok.value

op = lambda s: some(lambda tok: tok.type == 'OP' and tok.value == s) >> tokval
op_ = lambda s: skip(op(s))
const = lambda x: lambda _: x

number = some(lambda tok: tok.type == 'NUMBER') >> tokval
var = some(lambda tok: tok.type == 'NAME') >> tokval
string = some(lambda tok: tok.type == 'STRING') >> tokval

po = op_('(')
pc = op_(')')

integer = oneplus(number)
atom =  var | string | number

@with_forward_decls
def _funcapp():
    return ((var|string|integer) + oneplus(var|string|integer|_funcapp)) | (po + _funcapp + pc)

@with_forward_decls
def _sexp():
    #           HEAD       ARGS
    return po + atom + many(atom|_sexp) + pc

@with_forward_decls
def _pure():
    return _funcapp | atom

def pure_parse(str):
	return _pure.parse(tokenize(str))

def sexp_parse(str):
	return _sexp.parse(tokenize(str))

def funcapp_parse(str):
	return _funcapp.parse(tokenize(str))
