import worksheet.js as js
import worksheet.exceptions as exception
from worksheet.utils import *

from django import template
from django.utils.safestring import SafeUnicode

#-------------------------------------------------------------
# Base Term Class 
#-------------------------------------------------------------

# Philosophy for Math Objects
#
# Objects should only be inherited if they follow the Liskov
# Substitution Principle i.e. 
#
# 1) Let q(x) be a property provable about objects x of type T.
#    Then q(y) should be true for objects y of type S where S is
#    a subtype of T.
#
# 2) Objects should define their own Pure translation functions.
#
# 3) If A is an object and B is a subclass of A, if A is 
#    strictly internal ( no Pure translation ) then B should 
#    be stricly internal.

class Term(object):
    '''The base class for all other math objects.'''

    args = None # Static arguments used to initialze object
    terms = []  # Term objects as arguments to
    group = None # Expressions that object is embeeded in
    parent = None

    # TODO: change id -> cid
    id = None # The unique ID used to track the object clientside
    idgen = None # A instance of a uid generator

    # Database index
    sid = None

    # HTML / HAML template used to render object
    html = load_haml_template('term.tpl')
    latex = None # LaTeX code used in rendering object
    css_class = None # Extra styling in addition to .term class

    javascript = SafeUnicode()
    javascript_template = js.javascript_template
    has_sort = False # Can be reordered with jQuery sortable

    side = None # 0 if on LHS, 1 if on RHS

    #############################################################
    ######### Pure Translation ##################################
    #############################################################

    # self.pure property is automatically scraped off the object
    # at program initialization and translated into a PureSymbol
    # instance which is stored in self.po
    #
    # self.pure *must* be unique and must also not conflict with
    # any reserved names in the Pure namespace
    # 
    # For example for Addition has Addition.pure = 'add' which
    # runs the command in pure_wrap PureSymbol('add') and stores
    # the resulting Cython object inside Addition.po . 
    # When the # Addition._pure_ method is called 
    # Addition.po( arg1, arg2 ) is instantiated 

    # This results in a pure function application pure_funcapp 
    # Addition.po( arg1.po, arg2.po ) 

    # Note: If no pure property is specified the object is
    # entirely internal and cannot be used except in Python

    pure = None # A string containing the name symbol in Pure
    po = None   # Reference to the type of object

    #############################################################
    ######### Essential Methods for All Math Objects ############
    #############################################################

    # Every interaction between Math Objects requires that these
    # methods exist

    def __init__(self,*args,**kwargs):
        raise Exception('Anonymous Term was caught with arguments ' + (args,kwargs))

    def _pure_(self):
        # This is not defeind explicityly for the reason that inheriting
        # the method to generate a Pure object will often result in very
        # unexpected consequences if you not well thought out. Just define
        # one for every object
        raise exception.PureError('No Pure representation of %s.' % self.classname)

    def _latex_(self):
        raise exception.PureError('No LaTeX representation of %s.' % self.classname)

    def _sage_(self):
        raise exception.PureError('No Sage representation of %s.' % self.classname)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group
            })

        #if self.javascript:
        #    return self.html.render(c) + self.get_javascript()
        #else:
        return self.html.render(c)

    @property
    def math(self):
        return self.get_math()

    def get_math(self):
        '''Generates the sexp that is parsable on the Javascript side'''

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

    def wrap(self,other):
        '''Take one object and wrap it in container object, return
        the resulting container'''
        return other(self)

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
                    "toplevel": False,
                    "args": self.args,
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

    def combine(self,other,context):
        return self.combine_fallback(other,context)

    def ui_sortable(self,other=None):
        self.ensure_id()
        other.ensure_id()

        self.has_sort = True
        self.javascript = js.make_sortable(self,other).get_html()
        return self.get_javascript()
