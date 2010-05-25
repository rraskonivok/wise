# -*- coding: utf-8 -*-

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

import traceback

from django import template
from django.utils import simplejson as json
from django.utils.safestring import SafeUnicode

#Our parser functions
import parser

#Used for hashing trees
from hashlib import sha1
from binascii import crc32

#The whole sage library (this takes some time)
import sage.all as sage

#-------------------------------------------------------------
# Utilities
#-------------------------------------------------------------

def errors(f):
    def wrapper(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except Exception,e:
            print e
            print traceback.print_exc()
            return HttpResponse('Server-side Error')
    return wrapper

def spaceiter(list):
    '''iterate over a list returning a space separated string'''
    return reduce(lambda a,b: a + ' ' + b, list)

#Memoize single argument function
def memoize(f):
    def wrapper(*args):
        if args[0] in memo:
            return memo[args[0]]
        else:
            result = f(*args)
            memo[args] = result
            return result
    return wrapper

def pairs(list):
    for i in range(len(list) - 1):
        yield (list[i],list[i+1])

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
# Sage Wrapper
#-------------------------------------------------------------

class NoWrapper(Exception):
    def __init__(self,expr):
        self.value = 'Unable to cast Sage Type to Internal: %s :: %s' % (expr , str(type(expr)))

    def __str__(self):
        return self.value

from sage.functions import trig
from sage.functions import log
from sage.symbolic import constants
from sage import symbolic

#Longterm Goal: Recursive descent isn't the fastest way to do
#this find a better way

# We could just walk the parse tree casting as we go along.

#ExpressionIterator may be a way to do this faster

def parse_sage_exp(expr):

    if type(expr) is sage.Expression:
        operator = expr.operator()
        operands = expr.operands()

        #Symbols
        if expr._is_symbol():
            return Variable(str(expr))

        #Rational Numbers

        #There has to be an less ugly way to check if a
        #number is rational or not
        elif bool(expr.denominator() != 1):
            num = parse_sage_exp(expr.numerator())
            den = parse_sage_exp(expr.denominator())
            return Fraction(num,den)

        #Numbers

        #Constants
        elif expr._is_constant():
            pyo = expr.pyobject()
            if type(pyo) is constants.Pi:
                return Pi('pi')

        elif expr._is_numeric():
            if expr.is_zero():
                return Zero()

            if expr<0:
                expr = sage.operator.abs(expr)
                return Negate(Numeric(str(expr)))
            return Numeric(str(expr))

        #Relational Structures (i.e. Equations, Inequalities...)
        elif expr.is_relational():
            lhs = LHS(parse_sage_exp(expr.lhs()))
            rhs = RHS(parse_sage_exp(expr.rhs()))
            return Equation(lhs,rhs)

        #Basic Algebraic Structures
        elif operator is sage.operator.add:
            return apply(Addition,map(parse_sage_exp,operands))

        elif operator is sage.operator.mul:
            if operands[-1] == -1:
                return Negate(apply(Product,map(parse_sage_exp,operands[0:-1])))
            return apply(Product,map(parse_sage_exp,operands))

        elif operator is sage.operator.div:
            return apply(Fraction,map(parse_sage_exp,operands))

        elif operator is sage.operator.pow:
            if operands[1] == -1:
                return apply(Fraction,[Numeric(1),parse_sage_exp(operands[0])])
            if operands[1] < -1:
                nexp = sage.operator.abs(operands[1])
                #Convert this into a Fraction
                return apply(Fraction,[Numeric(1),parse_sage_exp(operands[0])])
            return apply(Power,map(parse_sage_exp,operands))

        elif operator is sage.operator.neg:
            return apply(Negate,map(parse_sage_exp,operands))

        #Trigonometric Functions
        elif operator is trig.cos:
            return apply(Cosine,map(parse_sage_exp,operands))

        elif operator is trig.sin:
            return apply(Sine,map(parse_sage_exp,operands))

        elif operator is trig.tan:
            return apply(Tangent,map(parse_sage_exp,operands))

        elif operator is trig.sec:
            return apply(Secant,map(parse_sage_exp,operands))

        elif operator is trig.csc:
            return apply(Cosecant,map(parse_sage_exp,operands))

        elif operator is trig.cot:
            return apply(Cotangent,map(parse_sage_exp,operands))

        #Exponential & Logarithms

        elif operator is log.ln:
            return apply(Log,map(parse_sage_exp,operands))

        elif operator is log.exp and operands == [1]:
            return E()

        elif operator is symbolic.operators.FDerivativeOperator:
            return apply(FDiff,map(parse_sage_exp,operands))

        elif isinstance(operator,symbolic.function.SymbolicFunction):
            return FreeFunction(operator.name(),Variable(str(operands[0])))
            return Variable(str(operands[0]))

        elif type(operator) is symbolic.operators.FDerivativeOperator:
            arg1 = parse_sage_exp(operator.function())
            arg2 = parse_sage_exp(operands[0])
            return FDiff(arg2,arg1)

    elif type(expr) is sage.Integer:
        if expr<0:
            expr = sage.operator.abs(expr)
            return Negate(Numeric(str(expr)))
        return Numeric(str(expr))

    elif isinstance(expr,symbolic.function.SymbolicFunction):
        return Variable(expr.name())

    raise NoWrapper(expr)


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
# 
# Calling Sage or casting into Internal objects is expensive and
# so we try and do as much as we can with the syntax tree before
# casting.

class InternalMathObjectNotFound(Exception):
    pass

class Branch(object):
    # I believe this is a type of Hash tree, 
    # http://en.wikipedia.org/wiki/Hash_tree
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
            if type(ob) is str:
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
        #print (self.type,hex(hash(self)))

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
            if type(i) is type(self):
                for j in i.walk():
                    yield j
                yield i

    def walk_all(self):
        for i in self.args:
            if type(i) is type(self):
                for j in i.walk():
                    yield j
                yield i
            else:
                yield i

    def walk_args(self):
        for i in self.args:
            if type(i) is type(self):
                for j in i.walk():
                    yield j
            else:
                yield i

    def json(self):
        def f(x):
            if type(x) is type(self):

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
            if type(x) is type(self):
                i = x.json_flat(lst)
                return i
            else:
                return x

        lst.append({'name': self.id, 'type': self.type})
        map(f,self.args)
        return lst

    def eval_args(self):
        '''Create an instance of the node's type ( self.type )
        and pass the node's arguments ( self.args ) to the new
        instance'''

        # We call the evil eval a couple of times but it's OK
        # because any arguments are previously run through the
        # math syntax parser and if the user tries to inject
        # anything other than (Equation ...)  it will throw an
        # error and not reach this point anyways.

        #Evalute by descent
        def f(x):
            #print 'TYPE IS',x
            if (type(x) is str) or (type(x) is unicode):
                # The two special cases where a string in the
                # parse tree is not a string
                if x == 'Placeholder':
                    return Placeholder()
                elif x == 'None':
                    return Empty()
                else:
                    return x
            elif type(x) is int:
                return x
            elif type(x) is type(self):
                '''create a new class from the Branch type'''
                try:
                    #print 'Trying to cast to',x.type

                    # TODO we have a way to check whether this object exists now

                    # TODO we could run through each of the
                    # namspaces instead, maybe that would be a
                    # little safer

                    inst = eval(x.type)
                    #print 'instance located',inst

                    #Descend into another branch 
                    return x.eval_args()
                except KeyError:
                    raise InternalMathObjectNotFound
                    print 'Could not find class: ',x.type
            else:
                print 'something strange is being passed'

        #See above if you are worried 
        obj = apply(eval(self.type),(map(f,self.args)))
        obj.hash = self.hash
        obj.id = self.id
        obj.idgen = self.idgen

        return obj

class ParseError(Exception):
    def __init__(self,expr):
        self.value = expr

    def __str__(self):
        return self.value

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
# Sugar Factories
#-------------------------------------------------------------

class UIDFactory:
    def __init__(self):
        self.increment = 0

    @errors
    def gen(self):
        self.increment +=1
        return 'uid'+str(self.increment)

uf = UIDFactory()

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

    def __str__(self):
        s = ''
        for key,value in super(prototype_dict,self).iteritems():
            s += ' %s: %s,' % (key,value)
        return '{%s}' % s

class bind():
    '''bind a method to element, context, or equation'''
    def __init__(self,obj,method):
        '''ui.item, ui.sender, original list '''
        pass

javascript_html = '''
{% autoescape off %}
<script language="javascript" type="text/javascript" data-type="ajax">{{javascript}}</script>
{% endautoescape %} 
'''

class make_sortable(object):
    '''Wrapper to produce the jquery command to make ui elements
    sortable/connected'''

    '''I'm thinking we should make a LOGGER... it should log the
    swapping of position of elements and record it in plain tex
    .... the same thing we applying functions ... allow user to
    change level of verbosity (omit basic algebra) and let the
    user merge lines of logs'''

    sortable_object = None
    connectWith = None
    cancel = '".ui-state-disabled"'
    helper = "'clone'"
    tolerance = '"pointer"'
    placeholder = '"helper"'
    #create a bind() method for these to connect to python methods
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
                                  #Rever is cool but buggy
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

term_html = '''
<span id="{{id}}" class="{{class}}{{sensitive}} term" math="{{math}}" math-type="{{type}}" title="{{type}}" math-meta-class="term" group="{{group}}">
<span class="noselect" >
${{latex}}$
</span>
</span> '''

class Term(object):

    args = None

    latex = '$Error$'
    is_negative = False
    html = template.Template(term_html)
    javascript_template = template.Template(javascript_html)
    group = None
    css_class = ''
    id = None
    terms = []
    javascript = SafeUnicode()
    has_sort = False

    _is_constant = False

    def __init__(self,*ex):
        print 'Anonymous Term was caught with arguments',ex

    #############################################################
    ######### Essential Methods for All Math Objects ############
    #############################################################

    # Every interaction between Math Objects requires that these
    # methods exist

    def _sage_(self):
        '''Returns the Sage equivalent of the object, this should
        roughly correspond to class in sage and should (if can be
        avoided) applying any other functions on the inputs'''
        pass

    def _latex_(self):
        '''LaTeX representation of the math object, this should
        only be used for export and shouldn't be called
        internally'''

    def get_html(self):
        self.ensure_id()
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname(),
            'group': self.group
            })

        if self.javascript:
            return self.html.render(c) + self.get_javascript()
        else:
            return self.html.render(c)

    def get_math(self):
        '''This generates the math that is parsable on the Javascript side'''

        #Container-type Objects, Example: (Addition 1 2 3)
        if len(self.terms) > 1:
            return '(' + self.classname() + ' ' + spaceiter(map(lambda o: o.get_math(), self.terms)) + ')'
        #Term-type Objects Example: (Numeric 3)
        elif len(self.terms) == 1:
            return '(' + self.classname() + ' ' + self.terms[0].get_math() + ')'
        #Terms with special arguments
        else:
            return '(' + self.classname() + ' ' + str(self.args) + ')'

    #############################################################

    def __add__(self,other):
        return Addition(*[self,other])

    def __mul__(self,other):
        return Product(*[self,other])

    def wrap(self,other):
        '''Take one object and wrap it in container object, return
        the container'''
        return other(self)

    def get_sensitive(self):
        if self.sensitive is False:
            return 'ui-state-disabled'
        else:
            return ''

    def ensure_id(self):
        '''Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one'''

        if not self.id:
            self.id = self.idgen.next()

    def negate(self):
        return Negate(self)

    def classname(self):
        return self.__class__.__name__

    def map_recursive(self,function):
        '''Apply a function to self and all descendants'''
        function(self)
        for term in self.terms:
            term.map_recursive(function)

    def get_javascript(self):
        c = template.Context({'javascript':self.javascript})
        return self.javascript_template.render(c)


#    def up(self):
#        return self.get_html()
#
#    def down(self,other):
#        return self.get_html()
#
#    def doubleclick(self):
#        '''when the user double clicks on the object'''



    def combine_fallback(self,other,context):
        '''Just slap an operator between two terms and leave it as is'''

        if context == 'Addition':
            if isinstance(other,Term):

                if type(other) is Negate:
                    result = self.get_html() + other.get_html()

                elif type(other) is Numeric:
                    if other.is_zero():
                        result = self.get_html()
                    else:
                        result = self.get_html() + infix_symbol_html(Addition.symbol) +  other.get_html()

                else:
                    result = self.get_html() + infix_symbol_html(Addition.symbol) +  other.get_html()

                return result
        if context == 'Product':
            if isinstance(other,Term):
                result = self.get_html() + infix_symbol_html(Product.symbol) +  other.get_html()
                return result
        if context == 'Wedge':
            if isinstance(other,Term):
                result = self.get_html() + infix_symbol_html(Wedge.symbol) +  other.get_html()
                return result

    @fallback(combine_fallback)
    def combine(self,other,context):
        pass

    def ui_id(self):
        '''returns the jquery code to reference to the html tag'''
        return '$("body").find("#%s")' % (self.id)

    def ui_bind(self):
        #bind a javscript level event (down,transfer list) to a
        #python side method of the object (i.e. divide, negate)...
        pass

    def ui_sortable(self,other=None):
        self.ensure_id()
        other.ensure_id()

        self.has_sort = True
        #TODO: add support for binding callbacks to python methods... later
        self.javascript = make_sortable(self,other).get_html()
        return self.get_javascript()

class PlaceholderInExpression(Exception):
    def __init__(self):
        self.value = 'A Placeholder was found in the equation and cannot be evaluated'

    def __str__(self):
        return self.value

placeholder_html = '''<span id="{{id}}" class="{{class}}{{sensitive}} drag_placeholder term" math="{{math}}" math-type="{{type}}" title="{{type}}" math-meta-class="term" group="{{group}}"></span>'''

class Placeholder(Term):
    '''A term that instantly gets removed when it's combined with
    anything else and anything can be substituted in for it
    during equation construction'''

    sensitive = False
    html = template.Template(placeholder_html)

    def __init__(self):
        self.latex = '$\\text{Placeholder}$'

    def _sage_(self):
        raise PlaceholderInExpression()

    def get_math(self):
        return '(Placeholder )'

class Empty(Term):
    sensitive = False
    def __init__(self):
        self.latex = '$\\text{Empty}$'

    def get_math(self):
        return 'Empty'

    def _sage_(self):
        return sage.var('P')

    def combine(self,other,context):
        return other.get_html()

#-------------------------------------------------------------
# Lower Level Elements 
#-------------------------------------------------------------

class Text(Term):
    type = 'text'
    sensitive = True

    def __init__(self,text):
        self.latex = '\\text{' + text + '}'

greek_alphabet = {
        'alpha': '\\alpha',
        'beta': '\\beta',
        'gamma': '\\gamma',
        'delta': '\\delta',
        'epsilon': '\\varepsilon',
        'pi': '\\pi',
        }

def greek_lookup(s):
    if s in greek_alphabet:
        return greek_alphabet[s]
    else:
        return s

class Base_Symbol(Term):
    sensitive = True
    def __init__(self,symbol):
        self.args = symbol
        self.symbol = greek_lookup(symbol)
        self.latex = greek_lookup(symbol)

    def _sage_(self):
        return sage.var(self.symbol)

class Greek(Base_Symbol):
    sensitive = True
    def __init__(self,symbol):
        self.symbol = symbol
        self.args = symbol
        #TODO: Just do a lookup table to avoid having to fall back on sage.latex
        self.latex = sage.latex(sage.var(symbol))

class Variable(Base_Symbol):
    assumptions = None
    bounds = None

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s$' % symbol
        self.args = str(symbol)

    def _sage_(self):
        return sage.var(self.symbol)


class RealVariable(Base_Symbol):
    '''It's like above but with the assumption that it's real'''
    pass

class Unit(Term):
    def __init__(self,symbol):
        self.symbol = symbol
        self.args = str(symbol)
        self.latex = sage.latex(symbol)

    def _sage_(self):
        import sympy.physics.units as units
        return sage.var(self.symbol)
        if self.symbol in dir(locals()['units']):
            unit = eval('units.'+self.symbol)
            return unit
        else:
            return sage.var(self.symbol)

    def get_sympy(self):
        import sympy.physics.units as units
        #Check if the units exists in sympy to prevent injection attacks
        if self.symbol in dir(locals()['units']):
            unit = eval('units.'+self.symbol)
            print 'unit',unit
            return unit

    def convert(self,other):
        '''Try to resolve the constant we need to multiply the constant by to
        convert one unit into another'''

        dv = self.get_sympy()/other.get_sympy()
        # Returns a set of units in the resultant division, if the
        # result is dimensionless => units resolve
        atoms = dv.atoms()
        if len(atoms) == 1:
            factor = atoms.pop()
            print factor
            return factor

            #TOOD: raise an error
            return false

physical_html = '''

<span id="{{id}}" math-meta-class="term" class="{{class}}{{sensitive}} term" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
<span class="parenthesis" title="{{type}}">
{{quantity}}
</span>
    <span class="unit" group="{{id}}" math-meta-class="unit">
    $$[[ {{unit}} ]]$$
    </span>
</span>

'''
class Physical_Quantity(Base_Symbol):
    '''(m/s).atoms() yields the set of base SI units .... ex (hbar).atoms()'''

    html = template.Template(physical_html)

    def __init__(self,quantity,units):
        self.ensure_id()
        self.terms = [quantity,units]

        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = units
        self.unit.group = self.id

    def _sage_(self):
        return self.quantity._sage_() * self.unit._sage_()

    def get_html(self):

        # So if we have a numeric quantity on the unit don't even
        # bother with (Physical_Quantity (Numeric 3.14)) stuff,
        # just treat the number at atomic

        if type(self.quantity) is Numeric:
            quantity_repr = '$$'+ str(self.quantity.number) + '$$'

        # If we have something more complex (Physical_Quantity
        # (Addition ... )) then have it act as a container 

        else:
            quantity_repr = self.quantity.get_html()

        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'quantity':quantity_repr,
            'math': self.get_math(),
            'type': self.classname(),
            'group': self.group,
            'unit': self.unit.symbol})

        return self.html.render(c)

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        if context == 'Addition':
            if isinstance(other,Physical_Quantity):
                #Same type of quantity (Length <-> Length)
                if isinstance(other,type(self)):

                    # A [unit] + B [unit] = (A+B)[unit]

                    combined = Addition(self.quantity,other.quantity)
                    combined.show_parenthesis = True
                    return Length(combined).get_html()

        return self.combine_fallback(other,context)

    def convert_unit(self,other):
        '''Scale the quantity by the necessary factor needed to convert between unit systems

        a = Numeric(3)
        Length(a,Unit('km')).convert_unit(Unit('m')) # Length('3000',Unit('m'))

        '''
        factor = self.unit.convert(other)
        self.quantity = Product(Numeric(factor),self.quantity)
        self.unit = other

class Length(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('m')):
        self.ensure_id()
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

class Momentum(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('N')):
        self.ensure_id()
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

class Mass(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('kg')):
        self.ensure_id()
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

class Velocity(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('ms')):
        self.quantity = quantity
        self.unit = unit
        self.terms = [quantity,self.unit]

#TODO Fix ugliness
power_html = '''<span id="{{id}}" group="{{group}}" class="term {{class}}{{sensitive}}" math-type="{{type}}" math-meta-class="term" math="{{math}}">
    <span class="base">{{base}}</span>
    <sup><span class="exponent">{{exponent}}</span></sup>
</span>
'''

class Power(Term):
    type = 'power'
    sensitive = True
    html = template.Template(power_html)

    def __init__(self,base,exponent):
        self.base = base
        self.exponent = exponent
        self.terms = [self.base, self.exponent]
        basetype = type(self.base)
        if basetype is Fraction or isinstance(self.base, Operation):
            self.base.show_parenthesis = True

    def _sage_(self):
        base = self.base._sage_()
        exponent = self.exponent._sage_()
        return sage.operator.pow(base,exponent)

    def get_html(self):
        self.exponent.css_class = 'exponent'
        self.exponent.group = self.id
        self.base.css_class = 'exponent'
        self.base.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'group': self.group,
            'base': self.base.get_html(),
            'type': self.classname(),
            'exponent': self.exponent.get_html() })

        return self.html.render(c)

fraction_html = '''
<span id="{{id}}" class="fraction container" math-meta-class="term" math-type="{{type}}" math="{{ math }}" group="{{group}}">

<span class="num">
{{ num }}
</span>

<span class="den">
{{ den }}
</span>

</span>
'''

class Fraction(Term):
    type = "Fraction"
    sensitive = True
    html = template.Template(fraction_html)

    def __init__(self,num,den):
        self.ensure_id()
        self.num = num
        self.den = den
        self.den.css_class = 'middle'
        self.terms = [num,den]

    def _sage_(self):
        return self.num._sage_() / self.den._sage_()
        return sage.Rational((self.num._sage_() , self.den._sage_()))

    def get_html(self):
        self.num.group = self.id
        self.den.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'num': self.num.get_html(),
            'den': self.den.get_html(),
            'group': self.group,
            'type': self.classname()
            })

        return self.html.render(c)


    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        pass
        #TODO: This breaks a heck of a lot
        #if isinstance(other,Fraction):
        #    num = Addition(Product(self.num,other.den),Product(self.den,other.num))
        #    den = Product(self.den,other.den)
        #    return Fraction(num,den).get_html()
        #elif isinstance(other,Numeric):
        #    num = Addition(self.num,Product(self.den,other))
        #    den = self.den
        #    return Fraction(num,den).get_html()

numeric_html = '''
<span id="{{id}}" title="{{type}}" class="{{class}} {{sensitive}} term" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
<span class="noselect" >
${{latex}}$
</span>
</span>'''

class Numeric(Term):
    type = 'numeric'
    sensitive = True
    html = template.Template(numeric_html)

    _is_constant = True

    def __init__(self,number):

        # TODO We shouldn't assume integers
        self.number = int(number)
        self.args = str(number)
        self.latex = number

    def _sage_(self):
        return sage.Integer(self.number)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname(),
            'group': self.group})

        return self.html.render(c)

    def is_zero(self):
        return self.number == 0

    def is_one(self):
        return self.number == 1

    def negate(self):
        #Zero is its own negation
        if self.is_zero():
            return self
        else:
            return Negate(self)

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        if context == 'Addition':
            if self.is_zero():
                return other.get_html()

            elif isinstance(other,Numeric):
                return Numeric(self.number + other.number).get_html()

        elif context == 'Product':
            if isinstance(other,Numeric):
                if self.is_zero():
                    return self.get_html()
                if self.is_one():
                    return other.get_html()
                else:
                    return Numeric(self.number * other.number).get_html()

            elif isinstance(other,Base_Symbol):
                #Multiplication by zero clears symbols
                if self.is_zero():
                    return self.get_html()

#Constants should be able to be represented by multiple symbols

class Constant(Term):
    sensitive = True
    representation = None

    def __init__(self,*symbol):
        self.ensure_id()
        self.args = self.representation.args
        self.latex = self.representation.latex

class E(Constant):
    representation = Base_Symbol('e')

    def _sage_(self):
        return sage.exp(1)

class Pi(Constant):
    representation = Base_Symbol('pi')

    def _sage_(self):
        return sage.pi

class Khinchin(Constant):
    representation = Base_Symbol('K_0')

    def _sage_(self):
        return sage.khinchin

def Zero():
    return Numeric(0)

def One():
    return Numeric(1)

#-------------------------------------------------------------
# Top Level Elements
#-------------------------------------------------------------

class Workspace(object):
    type = None
    '''Types of equation layouts

    A = _  |  A = A'  |
           |    = A'' |

    A = B  |  A  = B
           |  A' = B'

    A = B  |  A - B = 0

    '''

equation_html = '''
    <tr id="{{id}}" class="equation" math="{{math}}" math-type="Equation">

    <td>
        <button class="ui-icon ui-icon-triangle-1-w" onclick="select_term(get_lhs(this))">{{lhs_id}}</button>
        <button class="ui-icon ui-icon-triangle-2-e-w" onclick="select_term(get_equation(this))">{{id}}</button>
        <button class="ui-icon ui-icon-triangle-1-e" onclick="select_term(get_rhs(this))">{{rhs_id}}</button>
    </td>
    <td>{{lhs}}</td>
    <td><span class="equalsign">$$=$$</span></td>
    <td>{{rhs}}</td>

    </tr>
'''

class Equation(object):
    '''A statement involving LHS = RHS'''
    lhs = None
    rhs = None
    html = template.Template(equation_html)
    id = None

    def __init__(self,lhs,rhs):
        self.rhs = rhs
        self.lhs = lhs
        self.math = '(Equation ' + self.lhs.get_math() + ' ' +self.rhs.get_math()  + ')'

    def get_math(self):
        return self.math

    def _sage_(self):
        return self.lhs._sage_() == self.rhs._sage_()

    def get_html(self):
        self.rhs.group = self.id
        self.lhs.group = self.id

        self.lhs.javascript = None
        self.rhs.javascript = None

        self.rhs.rhs.id = self.idgen.next()
        self.lhs.lhs.id = self.idgen.next()

        s1 = self.lhs.lhs.ui_sortable(self.rhs.rhs)
        s2 = self.rhs.rhs.ui_sortable(self.lhs.lhs)

        javascript = s1 + s2

        #If we have an Equation of the form A/B = C/D then we can
        #drag terms between the numerator and denominator
        if self.lhs.lhs.has_single_term() and self.rhs.rhs.has_single_term():
            #TODO: Change these to isinstance
            if type(self.lhs.lhs.terms[0]) is Fraction and type(self.rhs.rhs.terms[0]) is Fraction:

               lfrac = self.lhs.lhs.terms[0]
               rfrac = self.rhs.rhs.terms[0]

               lden = lfrac.den
               rden = rfrac.den

               lnum = lfrac.num
               rnum = rfrac.num

               #lnumm, ldenm = lnum.wrap(Product) , lden.wrap(Product)
               #rnumm, rdenm = rnum.wrap(Product) , rden.wrap(Product)

               if type(lnum) is not Product:
                   lfrac.num = lfrac.num.wrap(Product)

               if type(rnum) is not Product:
                   rfrac.num = rfrac.num.wrap(Product)

               if type(lden) is not Product:
                   lfrac.den = lfrac.den.wrap(Product)

               if type(rden) is not Product:
                   rfrac.den = rfrac.den.wrap(Product)

               if type(lnum) is Product or type(lnum) is Variable:
                   javascript += lnum.ui_sortable(rfrac.den)

               if type(rnum) is Product or type(rnum) is Variable:
                   javascript += rnum.ui_sortable(lfrac.den)

               if type(lden) is Product or type(lden) is Variable:
                   javascript += lden.ui_sortable(rfrac.num)

               if type(rden) is Product or type(rden) is Variable:
                   javascript += rden.ui_sortable(lfrac.num)


        c = template.Context({
            'id': self.id,
            'rhs_id': self.rhs.id,
            'lhs_id': self.lhs.id,
            'math': self.math,
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html()
            })

        return self.html.render(c)

    def ensure_id(self):
        '''Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one'''

        if not self.id:
            self.id = self.idgen.next()

    def down(self,other):
        if type(other) is Numeric:
            self.lhs = LHS(*[Fraction(term,other) for term in self.lhs.terms])
            self.rhs = RHS(*[Fraction(term,other) for term in self.rhs.terms])
            self.rhs.group = self.id
            self.lhs.group = self.id

        return self.get_html()

rhs_html = '''
<span id='{{id}}' math-type="RHS" math-meta-class="side" math="{{math}}" group="{{group}}" class="container">
    {% autoescape off %}
    {{rhs}}
    {% endautoescape %}
</span>

'''

class RHS(Term):
    html = template.Template(rhs_html)

    def __init__(self,*terms):
        self.rhs = Addition(*terms)
        self.terms = [self.rhs]

    def _sage_(self):
        return self.rhs._sage_()

    def get_html(self):
        self.rhs.group = self.id

        c = template.Context({
            'id': self.id,
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname(),
            'group': self.group,
            'rhs': self.rhs.get_html()
            })

        return self.html.render(c)

lhs_html = '''
<span id='{{id}}' math-type="LHS" math-meta-class="side" math="{{math}}" group="{{group}}" class="container" >
    {% autoescape off %}
    {{lhs}}
    {% endautoescape %}
</span>
'''

class LHS(Term):
    html = template.Template(lhs_html)

    def __init__(self,*terms):
        self.lhs = Addition(*terms)
        self.terms = [self.lhs]

    def _sage_(self):
        return self.lhs._sage_()

    def get_html(self):
        self.lhs.group = self.id

        c = template.Context({'id': self.id, 'latex':self.latex, 'math': self.get_math(), 'type': self.classname(), 'group': self.group, 'lhs': self.lhs.get_html()})
        return self.html.render(c)

operation_html_postfix = '''
<span id="{{id}}" math-meta-class="term" class="term {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    <span class="parenthesis">
    {{operand}}
    </span>

    <span class="operator" math-type="operator" math-meta-class="operator" group="{{id}}">
    $${{symbol}}$$
    </span>
</span>
'''

operation_html_prefix = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    <span class="operator {{class}}" math-type="operator"
        math-meta-class="operator" group="{{id}}" title="{{type}}" >$${{symbol}}$$
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

operation_html_sandwich = '''
    <span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    <span class="operator" math-type="operator" math-meta-class="operator" group="{{id}}" title="{{type}}">$${{symbol}}$$</span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="parenthesis">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

    {{tail}}
    </span>
'''

#The unicode here comes from cmex10 font for parentheses

operation_html_infix = '''
    <span math-meta-class='term' id="{{id}}" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    {% if parenthesis %}

    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>

    {% endif %}

    {% for o in operand %}
    {{ o }}
    {% if not forloop.last %}
    <span id="{{ forloop.counter }}" class="ui-state-disabled infix" math-type='times' math-meta-class='sugar'>$${{symbol}}$$</span>
    {% endif %}
    {% endfor %}

    {% if parenthesis %}

    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>

    {% endif %}
    </span>
    {{jscript}}
'''

def infix_symbol_html(symbol):
    return '''<span class="ui-state-disabled infix term" math-type='infix' math-meta-class='sugar'>$${{%s}}$$</span>''' % symbol

#-------------------------------------------------------------
# Operations
#-------------------------------------------------------------

class Operation(Term):
    '''An operator acting a term'''

    ui_style = 'prefix'

    symbol = None
    show_parenthesis = False
    recursive_propogation = False
    sortable = False

    #Arity of the operator
    arity = None

    is_linear = False
    is_bilinear = False
    is_commutative = False
    is_anticommutative = False

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id

        #We should define a class so that we can do substitutions
        #later... based on whether or not the terms are commutative
        # ... define a == type

        self.terms = [self.operand]

    def action(self,operand):
        return self.get_html()

#    def propogate(self):
#        return self.get_html()

    def get_html(self):

        for term in self.terms:
            term.group = self.id

        # If a parent element has already initiated a sort (i.e
        # like Equation does) then don't overwrite that
        # javascript.
        if self.sortable and not self.has_sort:
            self.ui_sortable()

        #Infix Formatting
        if self.ui_style == 'infix':
            self.html = template.Template(operation_html_infix)
            objects = [o.get_html() for o in self.terms]

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname(),
                'group': self.group,
                'operand': objects,
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'jscript': self.get_javascript(),
                'class': self.css_class
                })

            return self.html.render(c)

        #"Sandwich" Formatting
        elif self.ui_style == 'sandwich':
            self.html = template.Template(operation_html_sandwich)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname(),
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'tail': self.tail.get_html(),
                'parenthesis': self.show_parenthesis
                })

            return self.html.render(c)

        #Prefix Formatting
        elif self.ui_style == 'prefix':
            self.html = template.Template(operation_html_prefix)

            if not self.css_class:
                self.css_class = 'middle'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname(),
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Postfix Formatting
        elif self.ui_style == 'postfix':
            self.html = template.Template(operation_html_postfix)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname(),
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        return self.html.render(c)

    def get_symbol(self):
        return self.symbol

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        return obj.get_html()

    def has_single_term(self):
        if len(self.terms) == 1:
            return True

class Unary_Operator(Term):
    arity = 1
    pass

class Binary_Operator(Term):
    arity = 2
    pass

class Ternary_Operator(Term):
    arity = 3
    pass

class Nary_Operator(Term):
    pass

class Gradient(Operation):
    ui_style = 'prefix'
    symbol = '\\nabla'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
        #TODO
        return sage.var('z')

class Addition(Operation):
    ui_style = 'infix'
    symbol = '+'
    show_parenthesis = False

    def __init__(self,*terms):
        self.terms = list(terms)

        #If have nested Additions collapse them Ex: 
        #(Addition (Addition x y ) ) = (Addition x y)

        if len(terms) == 1:
            if type(terms[0]) is Addition:
                self.terms = terms[0].terms

        #for term in self.terms:
        #    term.group = self.id

        self.operand = self.terms
        #self.ui_sortable()

    def __add__(self,other):
        if type(other) is Addition:
            self.terms.extend(other.terms)
            return self

    def _sage_(self):
        #Get Sage objects for each term
           sterms = map(lambda o: o._sage_() , self.terms)
           return reduce(sage.operator.add, sterms)

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        #If an object is dragged between sides of the equation negate the object

        if sender_context == 'LHS' or sender_context == 'RHS':
            obj = obj.negate()
            return obj.get_html()
        else:
            return obj.get_html()

    def remove(self,obj,remove_context):
        '''If we drag everything form this side of the equation
        zero it out'''

        if type(self.terms[0]) is Empty:
            zero = Numeric(0)
            return zero.get_html()

class Product(Operation):
    ui_style = 'infix'
    symbol = '\\cdot'
    show_parenthesis = False

    def __init__(self,*terms):
        self.ensure_id()
        self.terms = list(terms)

        #Pull constants out front
        #sorts by truth value with True's ordered first
        self.terms = sorted(self.terms, key=lambda term: not term._is_constant)

        for term in self.terms:
            term.group = self.id
            if type(term) is Addition:
                term.show_parenthesis = True
        self.operand = self.terms
        self.ui_sortable()

    def remove(self,obj,remove_context):

        if type(self.terms[0]) is Empty:
            return One().get_html()

    def _sage_(self):
        #Get Sage objects for each term
       sterms = map(lambda o: o._sage_() , self.terms)
       return reduce(sage.operator.mul, sterms)

class FreeFunction(Operation):
    ui_style = 'prefix'
    show_parenthesis = True

    def __init__(self,symbol,operand):
        self.ensure_id()
        if symbol is not Base_Symbol:
            symbol = Base_Symbol(symbol)
        self.symbol = symbol.symbol
        self.operand = operand
        self.operand.group = self.id
        self.terms = [symbol,self.operand]

    def _sage_(self):
       return sage.sin(self.operand._sage_())

class Log(Operation):
    ui_style = 'prefix'
    symbol = '\\log'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.log(self.operand._sage_())

class Sine(Operation):
    ui_style = 'prefix'
    symbol = '\\sin'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.sin(self.operand._sage_())

class Cosine(Operation):
    ui_style = 'prefix'
    symbol = '\\cos'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.cos(self.operand._sage_())

class Tangent(Operation):
    ui_style = 'prefix'
    symbol = '\\tan'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.tan(self.operand._sage_())

class Secant(Operation):
    ui_style = 'prefix'
    symbol = '\\sec'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.sec(self.operand._sage_())

class Cosecant(Operation):
    ui_style = 'prefix'
    symbol = '\\csc'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.csc(self.operand._sage_())

class Cotangent(Operation):
    ui_style = 'prefix'
    symbol = '\\cot'
    show_parenthesis = True

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
       return sage.cot(self.operand._sage_())

class Negate(Operation):
    ui_style = 'prefix'
    symbol = '-'
    show_parenthesis = False
    css_class = 'negate'

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

        if type(self.operand) is Addition:
            self.show_parenthesis = True

    def _sage_(self):
        return sage.operator.neg(self.operand._sage_())

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        if context == 'Addition':
            if isinstance(other,Negate):
                ''' -A+-B = -(A+B)'''
                return Negate(Addition(self.operand, other.operand)).get_html()

    def negate(self):
        return self.operand

#    def propogate(self):
#        return self.get_html()

class Wedge(Operation):
    ui_style = 'infix'
    symbol = '\\wedge'
    show_parenthesis = True

    def __init__(self,*terms):
        self.ensure_id()
        self.terms = list(terms)
        for term in self.terms:
            term.group = self.id
        self.operand = self.terms
        self.ui_sortable()

    def _sage_(self):
        #Get Sage objects for each term
        #TODO, this should be a wedge product
        sterms = map(lambda o: o._sage_() , self.terms)
        return sage.operator.add(*sterms)

class Laplacian(Operation):
    ui_style = 'prefix'
    symbol = '\\nabla^2'

    def __init__(self,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

class Differential(Operation):
    ui_style = 'prefix'
    symbol = 'd'
    show_parenthesis = False
    css_class = ''

    def __init__(self,variable):
        self.ensure_id()

        self.variable = variable
        self.operand = self.variable

        self.operand.group = self.id
        self.terms = [self.operand]

    def _sage_(self):
        #TODO: Does sage have a class for infinitesimals?
        return self.variable._sage_()

class Integral(Operation):
    ui_style = 'sandwich'
    symbol = '\\int'
    show_parenthesis = False

    def __init__(self,operand,differential):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id
        self.differential = differential
        self.differential.group = self.id
        self.differential.operand.sensitive = False
        self.differential.css_class = 'baseline'

        # The trailing differential dX
        self.tail = self.differential

        self.terms = [self.operand, self.tail]

    def _sage_(self):
        return sage.integral(self.operand._sage_(),
                self.differential._sage_())

#Differentiation has a slightly different setup than the other
#prefix operators

diff_html = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    <span class="operator middle" math-type="operator" math-meta-class="operator" group="{{id}}" title="{{type}}" >
        <span class="num">
        $$ \partial $$
        </span>

        <span class="den">
        <span class="math term">\partial</span>{{ differential }}
        </span>
    </span>

    {% if parenthesis %}
        <span class="ui-state-disabled pnths left">
           &Ograve;
        </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

class Diff(Operation):

    '''To do standard derivatives

    y=Function('y')(x)
    x=Symbol('x')
    diff(y*x,x)
    '''

    ui_style = 'prefix'

    def __init__(self,differential,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id

        self.differential = differential
        self.differential.group = self.id

        self.terms = [self.differential, self.operand]

    def _sage_(self):
        return sage.diff(self.operand._sage_(),
                self.differential._sage_())

    def get_html(self):
        self.html = template.Template(diff_html)

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'type': self.classname(),
            'group': self.group,
            'operand': self.operand.get_html(),
            'symbol': self.symbol,
            'parenthesis': self.show_parenthesis,
            'class': self.css_class,
            'differential': self.differential.get_html()
            })

        return self.html.render(c)

    def action(self):
        #Take the derivative
        deriv = sympify(self.sympy)
        #Cast it to internal types
        newterm = sympy2parsetree(deriv)
        return newterm.get_html()

    def propogate(self):

        #Propagates differentiation by descent

        if type(self.operand) is Addition:
            # Linearity of Differentiation: 
            # d/dx ( A + B + C ) ---> ( d/dx A + d/dx B + d/dx C) 

            split = map(Diff,self.operand.terms)
            split = map(lambda obj: obj.propogate(), split)
            return Addition(*split)

        elif type(self.operand) is Product:
            ''' Product Rule'''
            def leibniz(f,g):
                cross1 = Diff(f).propogate()
                cross2 = Diff(g).propogate()

                cross_result = cross1 * g + f * cross2
                cross_result.show_parenthesis = True
                return cross_result

            newterms = reduce(leibniz,self.operand.terms)
            return Addition(newterms)

        #elif type(self.operand) is Fraction:
        #    def leibniz(f,g):
        #        cross = Addition( Product(Diff(f),g) , Product(f,Diff(g)) )
        #        cross.show_parenthesis = True
        #        return cross

        #    newnum = leibniz(self.operand.num,self.operand.den)
        #    newden = Product(self.operand.num,self.operand.den)
        #    return Fraction(newnum,newden).get_html()

        #elif type(self.operand) is Base_Symbol:
        #    if self.operand.symbol == self.variable:
        #        return One().get_html()
        #    else:
        #        #This is partial differetiation
        #        return Zero().get_html()

        elif type(self.operand) is Numeric:
            return Zero()

        else:
            #Just leave the operator in since we can't do anything meaningful with it
            return self

fdiff_html = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    <span class="operator middle" math-type="operator" math-meta-class="operator" group="{{id}}" title="{{type}}" >
        <span class="num">
        $$ d $$
        </span>

        <span class="den">
        <span class="math term">d </span>{{ differential }}
        </span>
    </span>

    {% if parenthesis %}
        <span class="ui-state-disabled pnths left">
           &Ograve;
        </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

class FDiff(Operation):

    '''To do standard derivatives

    y=Function('y')(x)
    x=Symbol('x')
    diff(y*x,x)
    '''

    ui_style = 'prefix'

    def __init__(self,differential,operand):
        self.ensure_id()
        self.operand = operand
        self.operand.group = self.id

        self.differential = differential
        self.differential.group = self.id

        self.terms = [self.differential, self.operand]

    def _sage_(self):
        expr = self.operand._sage_()
        vrs = expr.variables()

        d = self.differential._sage_().variables()

        # Symmetric difference between the two sets
        fncs = set(vrs) - set(d)

        #Assume all variables are functions of the differential
        #variable

        # This produces objects in the global namespace uses
        # function_factory
        subs = map(lambda x: x==sage.function(str(x))(d[0]) ,fncs)
        for sub in subs:
            expr = expr.subs(sub)

        return sage.diff(expr, self.differential._sage_())

    def get_html(self):
        self.html = template.Template(fdiff_html)

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'type': self.classname(),
            'group': self.group,
            'operand': self.operand.get_html(),
            'symbol': self.symbol,
            'parenthesis': self.show_parenthesis,
            'class': self.css_class,
            'differential': self.differential.get_html()
            })

        return self.html.render(c)

    def action(self):
        #Take the derivative
        deriv = sympify(self.sympy)
        #Cast it to internal types
        newterm = sympy2parsetree(deriv)
        return newterm.get_html()

    def propogate(self):

        #Propagates differentiation by descent

        if type(self.operand) is Addition:
            # Linearity of Differentiation: 
            # d/dx ( A + B + C ) ---> ( d/dx A + d/dx B + d/dx C) 

            split = map(Diff,self.operand.terms)
            split = map(lambda obj: obj.propogate(), split)
            return Addition(*split)

        elif type(self.operand) is Product:
            ''' Product Rule'''
            def leibniz(f,g):
                cross1 = Diff(f).propogate()
                cross2 = Diff(g).propogate()

                cross_result = cross1 * g + f * cross2
                cross_result.show_parenthesis = True
                return cross_result

            newterms = reduce(leibniz,self.operand.terms)
            return Addition(newterms)

        #elif type(self.operand) is Fraction:
        #    def leibniz(f,g):
        #        cross = Addition( Product(Diff(f),g) , Product(f,Diff(g)) )
        #        cross.show_parenthesis = True
        #        return cross

        #    newnum = leibniz(self.operand.num,self.operand.den)
        #    newden = Product(self.operand.num,self.operand.den)
        #    return Fraction(newnum,newden).get_html()

        #elif type(self.operand) is Base_Symbol:
        #    if self.operand.symbol == self.variable:
        #        return One().get_html()
        #    else:
        #        #This is partial differetiation
        #        return Zero().get_html()

        elif type(self.operand) is Numeric:
            return Zero()

        else:
            #Just leave the operator in since we can't do anything meaningful with it
            return self

#-------------------------------------------------------------
# Transforms
#-------------------------------------------------------------

import algebra

#print [i.domain for i in algebra.mappings]
