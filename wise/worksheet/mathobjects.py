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

#For error reporting
import traceback

from django import template
from django.utils import simplejson as json
from django.utils.safestring import SafeUnicode
from django.utils.html import strip_spaces_between_tags as strip_whitespace

#Our parser functions
import parser

#Used for hashing trees
from hashlib import sha1
from binascii import crc32

import pure.algebra as pure

from wise.worksheet.models import Symbol, Function

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

def minimize_html(html):
    if not html:
        return None
    return strip_whitespace(html.rstrip('\n'))

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

class NoWrapper(Exception):
    def __init__(self,expr):
        self.value = 'Unable to cast Pure Type to Internal: %s :: %s' % (expr , str(type(expr)))

    def __str__(self):
        return self.value

def translate_pure(key):
    translation_table = {
            'add':Addition,
            'mul':Product,
            'pow':Power,
            'integral':Integral,
            'differential':Differential,
            'diff':Diff,
            'Neg':Negate,
            'rational':Fraction,
            'eq':Equation,
            'wiseref':RefSymbol,
            'wiserefop':RefOperator,
            'pi':Pi,
            'e':E,
            'Sin':Sine,
            'Cos':Cosine,
            'Tan':Tangent,
            }
    try:
        return translation_table[key]
    except KeyError:
        raise NoWrapper()

class PureError(Exception):
    def __init__(self,expr):
        self.value = expr

    def __str__(self):
        return self.value

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
# Parse Tree
#-------------------------------------------------------------

# Note:
# I was totally strung out on caffeine when I wrote all these
# recursive data structures and they seem to work flawlessly but
# I probably will never understand why again

# Create our parse tree structure, the Branch object simply holds
# the arguments before they are evaluated into internal Math
# objects

class InternalMathObjectNotFound(Exception):
    pass

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
        obj = apply(typ,(map(f,self.args)))
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

javascript_html = '''
{% autoescape off %}
<script language="javascript" type="text/javascript" data-type="ajax">{{javascript}}</script>
{% endautoescape %} 
'''

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
    idgen = None
    parent = None
    side = None # 0 if on LHS, 1 if on RHS

    def __init__(self,*ex):
        print 'Anonymous Term was caught with arguments',ex

    #############################################################
    ######### Essential Methods for All Math Objects ############
    #############################################################

    # Every interaction between Math Objects requires that these
    # methods exist

    def _pure_(self):
        raise PureError('No pure representation of %s.' % self.classname)

    def _latex_(self):
        raise PureError('No LaTeX representation of %s.' % self.classname)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group
            })

        if self.javascript:
            return self.html.render(c) + self.get_javascript()
        else:
            return self.html.render(c)

    def get_math(self):
        '''This generates the sexp that is parsable on the Javascript side'''

        #Container-type Objects, Example: (Addition 1 2 3)
        if len(self.terms) > 1:
            return '(' + self.classname + ' ' + spaceiter(map(lambda o: o.get_math(), self.terms)) + ')'
        #Term-type Objects Example: (Numeric 3)
        elif len(self.terms) == 1:
            return '(' + self.classname + ' ' + self.terms[0].get_math() + ')'
        #Terms with primitve arguments (no nested sexp)
        else:
            return '(' + self.classname + ' ' + str(self.args) + ')'

    def __repr__(self):
         return self.get_math()

    def set_side(self, side):
        for term in self.terms:
            term.side = side
            term.set_side(side)

    #############################################################

    #These can (and often should) be overloaded
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
        self.associate_terms()

    def associate_terms(self):
        '''Iterate through any child terms and associate their
        group property with the id of thet parent'''
        for term in self.terms:
            term.group = self.id

    def negate(self):
        return Negate(self)

    @property
    def classname(self):
        return self.__class__.__name__

    def map_recursive(self,function):
        '''Apply a function to self and all descendants'''
        function(self)
        for term in self.terms:
            term.map_recursive(function)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({"id": self.id,
                    "type": self.classname,
                    "children": [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def get_javascript(self):
        c = template.Context({'javascript':self.javascript})
        return self.javascript_template.render(c)

    def combine_fallback(self,other,context):
        '''Just slap an operator between two terms and leave it as is'''

        # This differs slightly from the the transformations called on
        # expressions in that we return both the json and the
        # html for the new object, the reason being that often
        # include syntatic sugar in the response sent to the
        # client 

        if context == 'Addition':
            if isinstance(other,Term):

                if type(other) is Negate:
                    # Don't add a plus sign if we have a negation
                    # to avoid verbose expressions like 3 + -4
                    result = self.get_html() + other.get_html()

                elif type(other) is Numeric:
                    if other.is_zero():
                        result = self.get_html()
                        other = None;
                    else:
                        result = self.get_html() + infix_symbol_html(Addition.symbol) + other.get_html()

                else:
                    result = self.get_html() + infix_symbol_html(Addition.symbol) +  other.get_html()

                return result,[self,other]

        elif context == 'Product':
            if isinstance(other,Term):
                result = self.get_html() + infix_symbol_html(Product.symbol) +  other.get_html()
                return result,[self,other]

        elif context == 'Wedge':
            if isinstance(other,Term):
                result = self.get_html() + infix_symbol_html(Wedge.symbol) +  other.get_html()
                return result,[self,other]

    @fallback(combine_fallback)
    def combine(self,other,context):
        pass

    def ui_id(self):
        '''Returns the jquery code to reference to the html tag'''
        return '$("#workspace").find("#%s")' % (self.id)

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
    '''A placeholder for substitution'''

    sensitive = False
    html = template.Template(placeholder_html)

    def __init__(self):
        self.latex = '$\\text{Placeholder}$'

    def _pure_(self):
        raise PlaceholderInExpression()

    def get_math(self):
        return '(Placeholder )'

class Empty(Term):
    sensitive = False
    def __init__(self):
        self.latex = '$\\text{Empty}$'

    def get_math(self):
        return 'Empty'

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

pureblob_template = '''
<div>
<img src="/static/pure.png" style="vertical-align: middle"/>
Pure Blob - <em>{{annotation}}
</div>
'''

class PureBlob(Term):
    '''Pure code with no internal representation, Pure Blob'''
    def __init__(self):
        pass

    def get_html(self):
        c = template.Context({'annotation': self.annotation})

        return template.Template(pureblob_template).render(c)

tex_template = '''
<span class="operator" math-type="operator" math-meta-class="operator" group="{{group}}" title="{{type}}">$${{tex}}$$</span>
'''

class Tex(object):
    '''LaTeX sugar for operators'''
    tex = None

    def __init__(self,tex):
        self.tex = tex

    def get_html(self):
        c = template.Context({
            'group': self.group,
            'type': 'Tex',
            'tex': self.tex})

        return template.Template(tex_template).render(c)

greek_alphabet = {
        'alpha': '\\alpha',
        'beta': '\\beta',
        'gamma': '\\gamma',
        'delta': '\\delta',
        'epsilon': '\\varepsilon',
        'pi': '\\pi',
        }

def greek_lookup(s):
    try:
        return greek_alphabet[s]
    except KeyError:
        return s

class Base_Symbol(Term):
    sensitive = True

    def __init__(self,symbol):
        self.args = "'%s'" % symbol
        self.symbol = greek_lookup(symbol)
        self.latex = greek_lookup(symbol)

    def _pure_(self):
        return pure.var(self.symbol)

class Greek(Base_Symbol):
    sensitive = True
    def __init__(self,symbol):
        self.symbol = symbol
        self.args = "'%s'" % symbol

#A free variable
class Variable(Base_Symbol):
    assumptions = None
    bounds = None

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s$' % symbol
        self.args = str(symbol)

    def _pure_(self):
        return pure.PureSymbol(self.symbol)

#Free abstract function (of a single variable at this time)
class FreeFunction(Base_Symbol):
    assumptions = None
    bounds = None

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s(u)$' % symbol
        self.args = str(symbol)

    def _pure_(self):
        #LHS
        if self.side is 0:
            return pure.PureSymbol(self.symbol + '@_')(pure.PureSymbol('u'))
        #RHS
        else:
            return pure.PureSymbol(self.symbol)(pure.PureSymbol('u'))

class Wildcard(Variable):
    def _pure_(self):
        return pure.PureSymbol('_')

#Reference to a user-defined symbol
class RefSymbol(Variable):
    assumptions = None
    bounds = None

    def __init__(self, obj):
        if isinstance(obj, unicode) or isinstance(obj,str):
            obj = Symbol.objects.get(id=int(obj))

        if isinstance(obj, Numeric):
            obj = Symbol.objects.get(id=obj.number)

        self.symbol = obj.tex
        self.latex = '$%s$' % self.symbol
        self.args = str(obj.id)

    def _pure_(self):
        return pure.ref(pure.PureInt(int(self.args)))

#A variable with a ::int flag restricting it to integers
class IntVariable(Variable):
    def _pure_(self):
        #Yah, this doesn't work
        return pure.env.eval('%s::int' % self.symbol)

class RealVariable(Base_Symbol):
    '''It's like above but with the assumption that it's real'''
    pass

class Unit(Term):
    def __init__(self,symbol):
        self.symbol = symbol
        self.args = str(symbol)

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
        self.terms = [quantity,units]

        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = units
        self.unit.group = self.id
        self.terms = [quantity,units]

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
            'type': self.classname,
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

class Length(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('m')):
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

class Momentum(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('N')):
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

class Mass(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('kg')):
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

class Time(Physical_Quantity):
    def __init__(self,quantity,unit=Unit('s')):
        self.quantity = quantity
        self.quantity.group = self.id
        self.unit = unit
        self.unit.group = self.id

        self.terms = [quantity,unit]

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

    def _pure_(self):
        return pure.powr(self.base._pure_() , self.exponent._pure_())

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
            'type': self.classname,
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
        self.num = num
        self.den = den
        self.den.css_class = 'middle'
        self.terms = [num,den]

    def _pure_(self):
       return pure.rational(self.num._pure_(), self.den._pure_())

    def get_html(self):
        self.num.group = self.id
        self.den.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'num': self.num.get_html(),
            'den': self.den.get_html(),
            'group': self.group,
            'type': self.classname
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

    def _pure_(self):
        return pure.PureInt(self.number)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
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
        self.args = self.representation.args
        self.latex = self.representation.latex

class E(Constant):
    representation = Base_Symbol('e')

    def _pure_(self):
        return pure.e()

class Pi(Constant):
    representation = Base_Symbol('pi')

    def _pure_(self):
        return pure.pi()

class Khinchin(Constant):
    representation = Base_Symbol('K_0')

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
    <tr id="{{id}}" class="equation" math="{{math}}" math-type="{{classname}}" toplevel="true">

    <td>
        <button class="ui-icon ui-icon-triangle-1-w" onclick="select_term(get_lhs(this))">{{lhs_id}}</button>
        <button class="ui-icon ui-icon-triangle-2-e-w" onclick="select_term(get_equation(this))">{{id}}</button>
        <button class="ui-icon ui-icon-triangle-1-e" onclick="select_term(get_rhs(this))">{{rhs_id}}</button>
    </td>
    <td>{{lhs}}</td>
    <td><span class="equalsign">$${{symbol}}$$</span></td>
    <td>{{rhs}}</td>
    <td class="guard">{{guard}}</td>
    <td class="annotation"><div contenteditable=true>{{annotation}}</div></td>

    </tr>
'''

class Equation(object):
    '''A statement relating some LHS to RHS'''
    lhs = None
    rhs = None
    html = template.Template(equation_html)
    id = None
    symbol = "="
    sortable = True
    parent = None
    side = None
    annotation = ''

    def __init__(self,lhs=None,rhs=None):

        # Conviencence definition so that we can call Equation()
        # to spit out an empty equation
        if not lhs:
            lhs = LHS(Placeholder())
        if not rhs:
            rhs = RHS(Placeholder())

        if not isinstance(lhs,LHS):
            lhs = LHS(lhs)

        if not isinstance(rhs,RHS):
            rhs = RHS(rhs)

        self.rhs = rhs
        self.lhs = lhs

        self.terms = [self.rhs, self.lhs]

    @property
    def math(self):
        l1 =' '.join([self.classname, self.lhs.get_math(), self.rhs.get_math()])
        return ''.join(['(',l1,')'])

    def __repr__(self):
         return self.math

    def _pure_(self):
        return pure.eq(self.lhs._pure_(),self.rhs._pure_())

    @property
    def classname(self):
        return self.__class__.__name__

    def set_side(self, side):
        for term in self.temrms:
            term.side = side
            term.set_side(side)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({"id": self.id,
                    "type": self.classname,
                    "toplevel": True,
                    "children": [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def get_html(self):
        self.rhs.id = self.idgen.next()
        self.lhs.id = self.idgen.next()

        self.rhs.group = self.id
        self.lhs.group = self.id

        self.lhs.javascript = None
        self.rhs.javascript = None

        self.rhs.rhs.id = self.idgen.next()
        self.lhs.lhs.id = self.idgen.next()

        self.rhs.rhs.associate_terms()
        self.lhs.lhs.associate_terms()

        if self.sortable:
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
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'classname': self.classname
            })

        return self.html.render(c)

    def ensure_id(self):
        '''Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one'''

        if not self.id:
            self.id = self.idgen.next()
        #self.lhs.idgen = self.idgen
        #self.rhs.idgen = self.idgen

        #self.lhs.ensure_id()
        #self.rhs.ensure_id()

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
        self.args = [self.rhs]
        self.side = 1
        self.rhs.side = 1
        self.rhs.parent = self

    def _pure_(self):
        return self.rhs._pure_()

    def get_html(self):
        self.rhs.group = self.id
        self.rhs.associate_terms()

        c = template.Context({
            'id': self.id,
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
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
        self.args = [self.lhs]
        self.side = 0
        self.lhs.side = 0
        self.lhs.parent = self

    #TODO: we NEED hashes on these, but because the Addition
    #contiainer is not created with the parser it doesn't get a
    #hash so we need to figure out a way to do that.
    #@property
    #def hash(self):
    #    pass

    def _pure_(self):
        return self.lhs._pure_()

    def get_html(self):
        self.lhs.group = self.id
        self.lhs.associate_terms()

        c = template.Context({
            'id': self.id,
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group,
            'lhs': self.lhs.get_html()
            })

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

operation_html_outfix = '''
    <span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {{symbol1}}

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

    {{symbol2}}

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

operation_html_sup = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    <sup>
    {{symbol1}}
    </sup>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

operation_html_sub = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    <sub>
    {{symbol1}}
    </sub>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

operation_html_latex = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="{{class}}">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

def infix_symbol_html(symbol):
    return '''<span class="ui-state-disabled infix term" math-type='infix' math-meta-class='sugar'>$${{%s}}$$</span>''' % symbol

definition_html = '''
    <tr id="{{id}}" class="equation" math="{{math}}"
    math-type="{{classname}}" toplevel="true" data-confluent="{{confluent}}" data-public="{{public}}">

    <td>
        <button class="ui-icon ui-icon-transferthick-e-w"
        onclick="apply_transform('ReverseDef',get_equation(this))">{{lhs_id}}</button>
        <button class="ui-icon ui-icon-arrow-4" onclick="select_term(get_equation(this))">{{id}}</button>
        <button class="confluence 
        {% if confluent %} 
        ui-icon ui-icon-bullet
        {% else %}
        ui-icon ui-icon-radio-off
        {% endif %}
        " onclick="toggle_confluence(get_equation(this))">{{id}}</button>
    </td>
    <td>{{lhs}}</td>
    <td><span class="equalsign">$${{symbol}}$$</span></td>
    <td>{{rhs}}</td>
    <td class="guard">{{guard}}</td>
    <td class="annotation"><div contenteditable=true>{{annotation}}</div></td>

    </tr>
'''

class Definition(Equation):
    symbol = ":="
    sortable = False
    html = template.Template(definition_html)
    confluent = True
    public = True

    def _pure_(self):
        if self.lhs.hash != self.rhs.hash:
            return pure.PureRule(self.lhs._pure_(),self.rhs._pure_())
        else:
            print "Definition is infinitely recursive."

    def get_html(self):

        self.rhs.id = self.idgen.next()
        self.lhs.id = self.idgen.next()

        self.rhs.group = self.id
        self.lhs.group = self.id

        self.lhs.javascript = None
        self.rhs.javascript = None

        self.rhs.rhs.id = self.idgen.next()
        self.lhs.lhs.id = self.idgen.next()

        self.rhs.rhs.associate_terms()
        self.lhs.lhs.associate_terms()

        c = template.Context({
            'id': self.id,
            'rhs_id': self.rhs.id,
            'lhs_id': self.lhs.id,
            'math': self.math,
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'confluent': int(self.confluent),
            'public': self.public,
            'classname': self.classname
            })

        return self.html.render(c)

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

    def __init__(self,*operands):
        if len(operands) > 1:
            self.terms = list(operands)
            self.operand = self.terms
        else:
            self.operand = operands[0]
            self.terms = [operands[0]]

    def action(self,operand):
        return self.get_html()

    def get_html(self):
        self.associate_terms()

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
                'type': self.classname,
                'group': self.group,
                'operand': objects,
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'jscript': self.get_javascript(),
                'class': self.css_class
                })

            return self.html.render(c)

        #Outfix Formatting
        elif self.ui_style == 'outfix':
            self.html = template.Template(operation_html_outfix)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'symbol2': self.symbol2.get_html(),
                'parenthesis': self.show_parenthesis
                })

            return self.html.render(c)

        #Prefix Formatting
        elif self.ui_style == 'prefix':
            self.html = template.Template(operation_html_prefix)

            #if not self.css_class:
            #    self.css_class = 'baseline'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
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
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Superscript Formatting
        elif self.ui_style == 'sup':
            self.html = template.Template(operation_html_sup)

            if not self.css_class:
                self.css_class = 'middle'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Subscript Formatting
        elif self.ui_style == 'sub':
            self.html = template.Template(operation_html_sub)

            if not self.css_class:
                self.css_class = 'middle'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })
        #Subscript Formatting
        elif self.ui_style == 'latex':
            self.html = template.Template(operation_html_latex)

            if hasattr(self.operand,'symbol'):
                self.operand.latex = "%s{%s}" % (self.symbol1, self.operand.symbol)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })
        else:
            print('Unknown operator class, should be (infix,postfix,prefix,outfix)')

        return self.html.render(c)

    def get_symbol(self):
        return self.symbol

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        return obj

    def has_single_term(self):
        if len(self.terms) == 1:
            return True

class RefOperator(Operation):
    def __init__(self, obj, *operands):
        if isinstance(obj, unicode) or isinstance(obj,str):
            obj = Function.objects.get(id=int(obj))

        if isinstance(obj, Numeric):
            obj = Function.objects.get(id=obj.number)

        if len(operands) > 1:
            self.terms = list(operands)
            self.operand = self.terms
        else:
            self.operand = operands[0]
            self.terms = [operands[0]]

        self.symbol = obj.symbol1
        self.ui_style = obj.notation
        self.index = obj.id

    @property
    def classname(self):
        return 'RefOperator__%d' % self.index

    def _pure_(self):
        args = [o._pure_() for o in self.terms]
        return pure.refop(pure.PureInt(int(self.index)))(*args)

class Gradient(Operation):
    ui_style = 'prefix'
    symbol = '\\nabla'
    show_parenthesis = True

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

class Addition(Operation):
    ui_style = 'infix'
    symbol = '+'
    show_parenthesis = False

    def __init__(self,*terms):
        self.terms = list(terms)

        #If we have nested Additions collapse them Ex: 
        #(Addition (Addition x y ) ) = (Addition x y)
        if len(terms) == 1:
            if type(terms[0]) is Addition:
                self.terms = terms[0].terms

        self.operand = self.terms
        make_sortable(self)

    def __add__(self,other):
        if type(other) is Addition:
            self.terms.extend(other.terms)
            return self

    def _pure_(self):
        # There is some ambiguity here since we often use an
        # addition operator of arity=1 to make UI magic happen
        # clientside, but we just eliminiate it when converting
        # into a expression
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return pure.add(*pterms)

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        #If an object is dragged between sides of the equation negate the object

        if sender_context == 'LHS' or sender_context == 'RHS':
            obj = obj.negate()
            return obj
        else:
            return obj

    def remove(self,obj,remove_context):
        '''If we drag everything form this side of the equation
        zero it out'''

        if type(self.terms[0]) is Empty:
            return Numeric(0)

class Product(Operation):
    ui_style = 'infix'
    symbol = '\\cdot'
    show_parenthesis = False

    def __init__(self,*terms):
        self.terms = list(terms)

        #Pull constants out front
        #sorts by truth value with True's ordered first
        self.terms = sorted(self.terms, key=lambda term: not term._is_constant)

        for term in self.terms:
            term.group = self.id
            if type(term) is Addition:
                term.show_parenthesis = True
        self.operand = self.terms
        #self.ui_sortable()

    def remove(self,obj,remove_context):
        if type(self.terms[0]) is Empty:
            return One()

    def _pure_(self):
        # There is some ambiguity here since we often use an
        # addition operator of arity=1 to make UI magic happen
        # clientside, but we just eliminiate it when converting
        # into a expression
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return pure.mul(*pterms)

class Log(Operation):
    ui_style = 'prefix'
    symbol = '\\log'
    show_parenthesis = True

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

class TrigFunction(Operation):
    ui_style = 'prefix'
    show_parenthesis = True
    css_class = 'baseline'

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

class Vector(Operation):
    ui_style = 'latex'
    symbol1 = '\\vec'

class Sine(TrigFunction):
    ui_style = 'prefix'
    symbol = '\\sin'

    def _pure_(self):
       return pure.sin(self.operand._pure_())

class Cosine(TrigFunction):
    symbol = '\\cos'

    def _pure_(self):
       return pure.cos(self.operand._pure_())

class Tangent(TrigFunction):
    symbol = '\\tan'

    def _pure_(self):
       return pure.tan(self.operand._pure_())

class Secant(TrigFunction):
    symbol = '\\sec'

    def _pure_(self):
       return pure.sec(self.operand._pure_())

class Cosecant(TrigFunction):
    symbol = '\\csc'

    def _pure_(self):
       return pure.csc(self.operand._pure_())

class Cotangent(TrigFunction):
    symbol = '\\cot'

    def _pure_(self):
       return pure.cot(self.operand._pure_())

class Sinh(TrigFunction):
    symbol = '\\sinh'

class Cosh(TrigFunction):
    symbol = '\\cosh'

class Tanh(TrigFunction):
    symbol = '\\tanh'

class Sech(TrigFunction):
    symbol = '\\sech'

class Csch(TrigFunction):
    symbol = '\\csch'

class Coth(TrigFunction):
    symbol = '\\coth'

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

    def _pure_(self):
       return pure.neg(self.operand._pure_())

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        ''' -A+-B = -(A+B)'''

        if context == 'Addition':
            if isinstance(other,Negate):
                return Negate(Addition(self.operand, other.operand))

    def negate(self):
        return self.operand

class Wedge(Operation):
    ui_style = 'infix'
    symbol = '\\wedge'
    show_parenthesis = True

    def __init__(self,*terms):
        self.terms = list(terms)
        for term in self.terms:
            term.group = self.id
        self.operand = self.terms
    #    self.ui_sortable()

class Dot(Operation):
    ui_style = 'infix'
    symbol = '\\cdot'
    show_parenthesis = True

    def __init__(self,*terms):
        self.terms = list(terms)
        for term in self.terms:
            term.group = self.id
        self.operand = self.terms

class Cross(Operation):
    ui_style = 'infix'
    symbol = '\\times'
    show_parenthesis = True

    def __init__(self,*terms):
        self.terms = list(terms)
        for term in self.terms:
            term.group = self.id
        self.operand = self.terms

class Laplacian(Operation):
    ui_style = 'prefix'
    symbol = '\\nabla^2'

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

class Differential(Operation):
    ui_style = 'prefix'
    symbol = 'd'
    show_parenthesis = False
    css_class = ''

    def __init__(self,variable):

        self.variable = variable
        self.operand = self.variable

        self.operand.group = self.id
        self.terms = [self.operand]

    def _pure_(self):
        return pure.differential(self.variable._pure_())

class Dagger(Operation):
    ui_style = 'sub'
    symbol1 = Tex('x')

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.symbol1.group = self.id

        self.terms = [self.operand]

class Integral(Operation):
    ui_style = 'outfix'
    symbol1 = Tex('\\int')
    show_parenthesis = False

    def __init__(self,operand,differential):
        self.operand = operand
        self.operand.group = self.id
        self.differential = differential
        self.differential.group = self.id
        self.differential.operand.sensitive = False
        self.differential.css_class = 'baseline'

        # The trailing differential dX
        self.symbol1.group = self.id
        self.symbol2 = self.differential

        self.terms = [self.operand, self.differential]

    def _pure_(self):
        return pure.integral(self.operand._pure_(), self.differential._pure_())

class Abs(Operation):
    ui_style = 'outfix'
    symbol1 = Tex('|')
    symbol2 = Tex('|')

    def __init__(self, operand):
        self.operand = operand
        self.operand.group = self.id

        self.symbol1.group = self.id
        self.symbol2.group = self.id
        self.terms = [self.operand]

    def _pure_(self):
        return pure.abs(self.operand._pure_())

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

    ui_style = 'prefix'

    def __init__(self,differential,operand):
        self.operand = operand
        self.differential = differential
        self.terms = [self.differential, self.operand]

    def _pure_(self):
        return pure.diff(
                   self.operand._pure_(),
                   self.differential._pure_()
               )

    def get_html(self):
        self.html = template.Template(diff_html)
        self.operand.group = self.id
        self.differential.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group,
            'operand': self.operand.get_html(),
            'symbol': self.symbol,
            'parenthesis': self.show_parenthesis,
            'class': self.css_class,
            'differential': self.differential.get_html()
            })

        return self.html.render(c)

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
        self.operand = operand
        self.operand.group = self.id

        self.differential = differential
        self.differential.group = self.id

        self.terms = [self.differential, self.operand]

    def get_html(self):
        self.html = template.Template(fdiff_html)

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'type': self.classname,
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
