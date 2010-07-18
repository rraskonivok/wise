'''
Wise
Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import operator
from tokenize import generate_tokens
from StringIO import StringIO
from pprint import pformat
from funcparserlib.parser import some, a, many, skip, finished, maybe, forward_decl, with_forward_decls
from funcparserlib.util import pretty_tree
import token
import funcparserlib

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

#Lexar parser
def tokenize(s):
    'str -> [Token]'
    return list(Token(*t)
        for t in generate_tokens(StringIO(s).readline)
        if t[0] not in [token.NEWLINE])

def tokval(tok):
    'Token -> str'
    return tok.value

op = (lambda s: some(lambda tok: tok.type == 'OP' and tok.value == s) >> tokval)
op_ = lambda s: skip(op(s))
const = lambda x: lambda _: x

makeop = lambda s, f: op(s) >> const(f)

add = makeop('+', operator.add)
sub = makeop('-', operator.sub)
mul = makeop('*', operator.mul)
div = makeop('/', operator.div)
pow = makeop('**', operator.pow)

unarg = lambda f: lambda x: f(*x)
eval_expr = unarg(lambda a, f, b: f(a, b))

number = some(lambda tok: tok.type == 'NUMBER') >> tokval
var = some(lambda tok: tok.type == 'NAME') >> tokval
string = some(lambda tok: tok.type == 'STRING') >> tokval
operator = add | sub | mul | div | pow
expr = (var | number) + many(operator + (var | number | string))
po = op_('(')
pc = op_(')')

@with_forward_decls
def primary():
    return (var + many(var|string|number|primary)) | (po + primary + pc)

toplevel = primary

def eq_parse(str):
	return toplevel.parse(tokenize(str))
