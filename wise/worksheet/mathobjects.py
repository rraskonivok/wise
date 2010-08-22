# -*- coding: utf-8 -*-

'''
Wise
Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
'''

#For error reporting
import traceback

from django import template
from django.utils import simplejson as json
from django.utils.html import strip_spaces_between_tags as strip_whitespace

#Our parser functions
import parser

#Used for hashing trees
from hashlib import sha1
from binascii import crc32
from operator import xor 

from wise.worksheet.utils import *
from wise.worksheet.models import Symbol, Function, Rule

import pure_wrap

#-------------------------------------------------------------
# Utilities
#-------------------------------------------------------------

def html(*objs):
    if not objs:
        return None
    new_html = [];

    for obj in objs:
        new_html.append(minimize_html(obj.get_html()))

    return ''.join(new_html)

def purify(obj):
    return obj._pure_()

def pairs(list):
    for i in range(len(list) - 1):
        yield (list[i],list[i+1])

def hasharray(lst):
    return hash(reduce(xor, lst))

def fallback(fallback):
    '''Try to run f, if f returns None or False then run fallback'''
    def options(f):
        def wrapper(self,*args,**kwargs):
            if f(self,*args,**kwargs) is None:
                return fallback(self,*args,**kwargs)
            else:
                return f(self,*args,**kwargs)
        return wrapper
    return options

#Wrapper to make crcdigest behave like hashlib functions
class crcdigest(object):
    def __init__(self):
        #crc32(0) = 0
        self.hash = 0

    def update(self,text):
        self.hash = crc32(text,self.hash)

    def hexdigest(self):
        return hex(self.hash)

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
        raise NoWrapper(key)


def parse_pure_exp(expr, uidgen=None):
    #Get the string representation of the pure expression
    parsed = ParseTree(str(expr))
    if uidgen:
        parsed.gen_uids(uidgen)
    else:
        print "You better be manually assigning UIDs or else!!!!"
    #Map into the Python wrapper classes
    return parsed.eval_pure()

#Convenience wrappers with more obvious names...
def pure_to_python(obj,uidgen=None):
    '''Maps a set of Pure objects (as translated by the Cython
    wrapper into internal Python objects'''
    return parse_pure_exp(obj,uidgen)

def python_to_pure(obj):
    '''Maps internal Python objects into their pure equivelents'''
    return obj._pure_()

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
# Parse Tree
#-------------------------------------------------------------

# Note:
# I was totally strung out on caffeine when I wrote all these
# recursive data structures and they seem to work flawlessly but
# I probably will never understand why again

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
    # collisions than CRC32. But it's much slower.

    def __init__(self,typ,args,parent):
        self.type = typ
        self.id = None

        self.valid = False
        self.hash = False
        self.commutative = False

        if self.type == 'Addition':
            self.commutative = True

        def descend(ob):
            if type(ob) is str or type(ob) is unicode:
                return ob
            else:
                #Yah, there is a serious functional slant to this
                return reduce(lambda a,b: Branch(a,b,self), ob)

        #Allow for the possibility of argument-less/terminal Branches
        if args:
            self.args = map(descend,args)
        else:
            self.args = []

        self.parent = parent

    def __repr__(self):
        return 'Branch: %s(%r)' % (self.type,self.args)

    def __getitem__(self,n):
        return self.args[n]

    def __hash__(self):
        return self.gethash()

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
        # complex for this to always work, but it is very useful
        # for substitutions on toplevel nodes like Equation.

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
        # Addition( x y ) and Multiplication( x y )
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

    def gen_uids(self,uid_generator):
        '''Take a uid generator and walk the tree assigning each
        node a unique id'''

        self.id = uid_generator.next()
        self.idgen = uid_generator

        for node in self.walk():
            node.id = uid_generator.next()
            # Give the element the uid generator so it can spawn
            # new elements that don't conflict in the HTML
            # id/namespace
            node.idgen = uid_generator


    def is_toplevel(self):
        return self.parent == None

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

                i = x.json()
                return i
            else:
                return x
        obj = map(f,self.args)
        return {'name': self.id, 'type': self.type , 'args': obj }

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        def f(x):
            if isinstance(x,Branch):
                i = x.json_flat(lst)
                return i
            else:
                return x

        lst.append({"id": self.id,
                    "type": self.type,
                    "children": [child.id for child in self.args if isinstance(child,Branch)]})

        map(f,self.args)
        return lst

    def eval_args(self):
        '''Create an instance of the node's type ( self.type )
        and pass the node's arguments ( self.args ) to the new
        instance'''

        # We call the evil eval a couple of times but it's OK
        # because any arguments are previously run through the
        # sexp parser and if the user tries to inject
        # anything other than (Equation ...)  it will throw an
        # error and not reach this point anyways.

        # Recursive descent
        def f(x):
            if isinstance(x,unicode) or isinstance(x,str):
                # The two special cases where a string in the
                # parse tree is not a string
                if x == 'Placeholder':
                    return Placeholder()
                elif x == 'None':
                    return Empty()
                else:
                    return x
            elif isinstance(x,int):
                return x
            elif isinstance(x,Branch):
                #create a new class from the Branch type
                try:
                    return x.eval_args()
                except KeyError:
                    raise InternalMathObjectNotFound
                    print 'Could not find class: ',x.type
            else:
                print 'something strange is being passed'

        #Ugly hack to pass database indices
        if '__' in self.type:
            ref,id = self.type.split('__')
            self.args.insert(0,id)
            obj = apply(eval(ref),(map(f,self.args)))
            obj.hash = self.gethash()
            obj.idgen = self.idgen
        else:
            obj = apply(eval(self.type),(map(f,self.args)))
            obj.hash = self.gethash()
            obj.id = self.id
            obj.idgen = self.idgen

        if hasattr(obj,'side') and (obj.side is not None):
            obj.set_side(obj.side)

        return obj

    def eval_pure(self):
        '''Like pure_eval but instead of mapping into internal
        python objects it maps into Pure Objects. This is used
        for when we run an expression through pure and want to
        map the result into something to use in Python.'''

        #Evalute by descent
        def f(x):
            #Ugly Hack
            if isinstance(x,str):
                if x.isdigit():
                    obj = Numeric(x)
                elif x in translation_table:
                    obj = translate_pure(x)()
                else:
                    obj = Variable(x)
                obj.idgen = self.idgen
                obj.id = self.idgen.next()
                return obj
            elif isinstance(x,Branch):
                '''create a new class from the Branch type'''
                try:
                    return x.eval_pure()
                except KeyError:
                    raise InternalMathObjectNotFound
                    print 'Could not find class: ',x.type
            else:
                print 'something strange is being passed'

        typ = translate_pure(self.type)

        try:
            obj = apply(typ,(map(f,self.args)))
        except TypeError:
            raise ParseError("Invalid function arguments: %s, %s" % (self.args, typ))

        obj.id = self.id
        obj.idgen = self.idgen

        return obj


def ParseTree(str):
    try:
        parsed = parser.eq_parse(str)
        return reduce(lambda type, args: Branch(type,args,None), parsed)
    except Exception, e:
        raise ParseError(str)

# Prints out a tree diagram of the parse tree with the
# hashes for each object Ex:
#
# Equation  ::  4028231753125593003
# |-- LHS  ::  2709287584732918745
# |   `-- Addition  ::  2709287584732918745
# |       `-- Integral  ::  2709287584732918745
# |           `-- Addition  ::  2709287584732918745
# |               `-- Greek  ::  2709287584732918745
# |                   `-- 'alpha'
# `-- RHS  ::  1318944168392674258
#     `-- Addition  ::  1318944168392674258
#         `-- Integral  ::  1318944168392674258
#             `-- Addition  ::  1318944168392674258
#                 `-- Greek  ::  1318944168392674258
#                     `-- 'beta'

def pretty(t):
    from funcparserlib.util import pretty_tree

    def kids(x):
        if isinstance(x,Branch):
            return x.args
        else:
            return []

    def show(x):
        if isinstance(x,Branch):
            return str(x.type) + '  ::  ' +  hash(x)
        else:
            return repr(x)

    return pretty_tree(t,kids,show)

#-------------------------------------------------------------
# JQuery Interfaces
#-------------------------------------------------------------

def jquery(obj):
    '''Returns a jquery "function" (i.e. $('#uid123') )  for a given object'''
    return '$("#%s")' % obj.id


class prototype_dict(dict):
    '''Python and Javascript dictionaries are similar except that
    python requires strings, this eliminates quotes in the
    __str__ representation

    Example:
    > a = prototype_dict()
    > a['foo'] = 'bar'
    > print a
    { foo : 'bar' }

    '''

    def __repr__(self):
        s = ''
        for key,value in super(prototype_dict,self).iteritems():
            s += ' %s: %s,' % (key,value)
        return '{%s}' % s

class bind():
    '''bind a method to element, context, or equation'''
    def __init__(self,obj,method):
        '''ui.item, ui.sender, original list '''
        pass


class make_sortable(object):
    '''Wrapper to produce the jquery command to make ui elements
    sortable/connected'''

    sortable_object = None
    connectWith = None
    cancel = '".ui-state-disabled"'
    helper = "'clone'"
    tolerance = '"pointer"'
    placeholder = '"helper"'
    onout = None
    onupdate = 'function(event,ui) { update($(this)); }'
    onreceive = 'function(event,ui) { receive(ui,$(this),group_id); }'
    onremove = 'function(event,ui) { remove(ui,$(this)); }'
    onsort = None
    forcePlaceholderSize = '"true"'
    forceHelperSize = '"true"'
    dropOnEmpty = '"true"'
    axis = '"false"'

    def __init__(self, sortable_object,
            ui_connected=None,
            onremove=None,
            onrecieve=None,
            onsort=None,
            onupdate=None):

        self.sortable_object = jquery(sortable_object)
        if ui_connected is None:
            self.connectWith = 'undefined'
            self.upupdate = 'undefined'
        else:
            self.connectWith = jquery(ui_connected)

    def get_html(self):
        options = prototype_dict({'placeholder': self.placeholder,
                                  'connectWith': self.connectWith,
                                  'forceHelperSize': self.forceHelperSize,
                                  'helper': self.helper,
                                  'tolerance': self.tolerance,
                                  'axis': self.axis,
                                  'update': self.onupdate,
                                  'receive': self.onreceive,
                                  'remove': self.onremove,
                                  'cancel': self.cancel,
                                  #Revert is cool but buggy
                                  #'revert': 'true',
                                  #'deactivate': self.onupdate,
                                  'forcePlaceholderSize': self.forcePlaceholderSize})

        # An inconceivable amount of time/pain went into finding
        # out that different browsers execute/run javascript
        # immediately as it is loaded in the dom thus selectors
        # that call objects that are farther down will be empty,
        # this is solved by running all scripts when the document
        # signals it is. 

        args = (self.sortable_object, self.connectWith,
                str(options))

        html = '$(document).ready(function(){make_sortable(%s,%s,%s);})'

        return html % args

class ParseError(Exception):
    def __init__(self,expr):
        self.value = expr

    def __str__(self):
        return self.value

class InternalMathObjectNotFound(Exception):
    pass

class PureError(Exception):
    def __init__(self,expr):
        self.value = expr

    def __str__(self):
        return self.value

class PlaceholderInExpression(Exception):
    def __init__(self):
        self.value = 'A Placeholder was found in the equation and cannot be evaluated'

    def __str__(self):
        return self.value

class NoWrapper(Exception):
    def __init__(self,expr):
        self.value = "No translation for %s" % expr

    def __str__(self):
        return self.value

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

import algebra

#print [i.domain for i in algebra.mappings]

#generate_translation(root=Term)
#generate_translation(root=Equation)
#generate_pure_objects(root=Term)
#generate_pure_objects(root=Equation)

