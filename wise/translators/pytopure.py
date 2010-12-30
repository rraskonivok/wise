# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from wise.worksheet.utils import *
import wise.worksheet.exceptions as exception

# i2p ~ Infix to Prefix
# p2i ~ Prefix to Infix
#from wise.pure.prelude import p2i, i2p

from wise.translators.mathobjects import translate_pure, pyobjects

from parser import sexp_parse, pure_parse

#Used for hashing trees
from hashlib import sha1

#-------------------------------------------------------------
# Parse Tree
#-------------------------------------------------------------

# Create our parse tree structure, the Branch object simply holds
# the arguments before they are evaluated into internal Math
# objects


class Branch(object):
    #
    #         O            The hash of a non-terminal node is
    #        / \           hash of its children's hashes.
    #       /   \
    #      O     O         Terminal nodes have carry a unicode
    #     /|\    |         string which is hashed yield the hash
    #    / | \   |         of the node.
    #   #  #  #  O
    #           / \        All nodes have carry a unicode
    #          /   \       string 'type' which is hashed
    #         #     #      into the node.

    # We use the SHA1 algorithm, since it likely to have
    # collisions than CRC32.

    atomic = False
    idgen = None

    def __init__(self, typ, args):
        self.type = typ
        self.id = None

        self.valid = False
        self.args = args
        self.arity = len(args)

        self.subterms = set([child for child in self.args if
            isinstance(child,Branch)])

        self.subatoms = set([child for child in self.args if
            not isinstance(child,Branch)])

    def __repr__(self):
        return '(%s,%r)' % (self.type,self.args)

    def __getitem__(self,n):
        return self.args[n]

    #def __hash__(self):
    #    return self.gethash()

    def gethash(self):

        #      Eq. 1     =      Eq. 2
        #       / \              / \
        #      /   \            /   \
        #    LHS   RHS         LHS   RHS
        #    /|\    |           |    /|\
        #   / | \   |           |   / | \
        #  x  y  z add         add x  y  z
        #          / \         / \
        #         /   \       /   \
        #        1     2     2     1
        #
        # The point of this hash function is so that equivalent
        # mathobjects "bubble" up through the tree. Since
        # addition is commutative:
        #
        # hash ( 1 + 0 ) = hash( 1 ) + hash ( 0 )
        #                = hash( 0 ) + hash ( 1 )
        #
        # Mathematical structures are in general much too
        # complex for this to be very usefull, but it is very
        # usefulfor substitutions on toplevel nodes like Equation.

        #HASH_ALGORITHM = sha1
        HASH_ALGORITHM = crcdigest

        if self.valid:
            return self.hash

        def f(x):
            if isinstance(x,unicode) or isinstance(x,str):
                digester = HASH_ALGORITHM()
                digester.update(x)
                return digester.hexdigest()
            else:
                return x.gethash()

        ls = map(f,self.args)
        digester = HASH_ALGORITHM()

        # Hashing the type assures that
        # Addition( x y ) and Product( x y )
        # yield different hashes
        digester.update(self.type)

        if self.commutative:
            sm = sum([int(hsh,16) for hsh in ls])
            digester.update(str(sm))
            self.hash = digester.hexdigest()
        else:
            for arg in ls:
                digester.update(arg)
            self.hash = digester.hexdigest()

        self.valid = True
        return self.hash

    def walk(self):
        for i in self.args:
            if isinstance(i,Branch):
                for j in i.walk():
                    yield j
                yield i

    def walk_all(self):
        for i in self.args:
            if isinstance(i,Branch):
                for j in i.walk():
                    yield j
                yield i
            else:
                yield i

    def walk_args(self):
        for i in self.args:
            if isinstance(i,Branch):
                for j in i.walk():
                    yield j
            else:
                yield i

    def json(self):
        def f(x):
            if isinstance(x,Branch):
                return x.json()
            else:
                return x

        obj = map(f,self.args)

        return { 'name': self.id,
                'type': self.type,
                'args': obj }

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        def f(x):
            if isinstance(x,Branch):
                return x.json_flat(lst)
            else:
                return x

        lst.append({"id": self.id,
                    "type": self.type,
                    "children": [child.id for child in self.subterms]})

        map(f, self.args)
        return lst

    def eval_args(self):
        '''Create an instance of the node's type ( self.type )
        and pass the node's arguments ( self.args ) to the new
        instance'''

        def f(x):
            if isinstance(x,unicode) or isinstance(x,str):
                return x
            elif isinstance(x,int) or isinstance(x,float):
                return x
            elif isinstance(x,Branch):
                return x.eval_args()

        type = pyobjects[self.type]

        if not type:
            raise Exception('Could not lookup Python class', self.type)
            return

        obj = type(*(f(arg) for arg in self.args))

        return obj

    def eval_pure(self):
        '''Like pure_eval but instead of mapping into internal
        python objects it maps into Pure Objects. This is used
        for when we run an expression through Pure and want to
        map the result into something to use in Python.'''

        #Evalute by descent
        def f(x):
            if isinstance(x,str):
                return x
            elif isinstance(x,int) or isinstance(x,float):
                return x
            elif isinstance(x,Branch):
                return x.eval_pure()

        type = translate_pure(self.type)
        obj = type(*(f(arg) for arg in self.args))

        return obj

def map_nullary(parsed):
    """ Recursively convert nullary functions to prefix form"""
    if isinstance(parsed,tuple):
        head = parsed[0]
        args = parsed[1]

        return Branch(head, [map_nullary(arg) for arg in args])
    else:
        atom = parsed
        if is_number(atom):
            return Branch('num',[atom])
        elif atom == 'ph':
            return Branch('ph',[])
        else:
            return Branch('var',[atom])

def make_sexp(parsed):
    """ Convert ParseTree into Branch objects"""
    if isinstance(parsed,tuple):
        head = parsed[0]
        args = parsed[1]

        return Branch(head, [make_sexp(arg) for arg in args])
    else:
        return parsed

def ParseTree(s, parser):
    """ Recursively maps the output of the sexp parser to
    expression tree Branch objects.
    """

    # the parser generates nested tuples, in the simplest case it
    # looks like:
    #
    # SEXP:
    # (head arg1 arg2 arg3)
    #
    # PARSER OUTPUT:
    # ( head [arg1, arg2, arg3] )
    #
    #  Which has tree form:
    #
    # head
    #   |-- 'arg1'
    #   |-- 'arg2'
    #   `-- 'arg3'
    #
    # For nested sexp it looks something like:
    #
    # SEXP:
    # ( head1 (head2 arg1 arg2) arg3 arg4 )
    #
    # PARSER OUTPUT:
    # ( head1 [(head2 [arg1,arg2]), arg3, arg4])
    #
    # head
    # |-- head2
    # |   |-- 'arg1'
    # |   `-- 'arg2'
    # |-- 'arg3'
    # `-- 'arg4'

    if parser == 'sexp':
        parsed = sexp_parse(s)
        return make_sexp(parsed)

    elif parser == 'pure':
        parsed = pure_parse(s)
        return map_nullary(parsed)

def parse_pure_exp(expr):
    'PureExpr -> Object'
    #Get the string representation of the pure expression
    parsed = ParseTree(str(expr),'pure')

    #Map into the Python wrapper classes
    return parsed.eval_pure()

def parse_sexp(sexp_str):
    'String -> Object'
    parsed = ParseTree(sexp_str, 'sexp')
    evaled = parsed.eval_args()
    return evaled

#Convenience wrappers with more obvious names...
def pure_to_python(obj, wrap_infix=True):
    """Maps a set of Pure objects (as translated by the Cython
    wrapper) into internal Python objects
    """

    if wrap_infix:
        return parse_pure_exp(i2p(obj))
    else:
        return parse_pure_exp(obj)

def python_to_pure(obj, wrap_infix=True):
    """Maps internal Python objects into their Pure equivelents"""

    if wrap_infix:
        return p2i(obj._pure_())
    else:
        return obj._pure_()

def is_valid_sexp(sexp):
    try:
        ParseTree(str(expr), 'sexp')
    except ParseError:
        return False
    return True

def is_valid_pure(code):
    try:
        ParseTree(str(code), 'pure')
    except ParseError:
        return False
    return True
