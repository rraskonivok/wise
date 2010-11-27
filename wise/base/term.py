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

    args = [] # Static arguments used to initialze object
    terms = []  # Term objects as arguments to
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
    show_parenthesis = False

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

    @property
    def classname(self):
        return self.__class__.__name__

    def _pure_(self):
        # This is not defeind explicityly for the reason that inheriting
        # the method to generate a Pure object will often result in very
        # unexpected consequences if not well thought out. Just define
        # one for every object you create
        raise exception.PureError('No Pure representation of %s.' % self.classname)

    def _latex_(self):
        raise exception.PureError('No LaTeX representation of %s.' % self.classname)

    def _sage_(self):
        raise exception.PureError('No Sage representation of %s.' % self.classname)

    def _isabelle_(self):
        raise exception.PureError('No Isabelle representation of %s.' % self.classname)

    def _openmath_(self):
        raise exception.PureError('No OpenMath representation of %s.' % self.classname)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class or '',
            'latex':self.latex,
            'type': self.classname,
            })

        return self.html.render(c)

    @property
    def math(self):
        return self.get_math()

    def get_math(self):
        '''Generates the sexp representation of the object

        The sexp is the universal storage format from which Wise can
        build any object up from scratch.
        '''

        # Container-type Objects: 
        # Examples: 
        #       (Addition 1 2 )
        #       (Addition (Addition x y) 2)
        if len(self.terms) > 1:
            return msexp(self, self.terms)

        # Term-type Objects 
        # Example: 
        #       (Numeric 3)

        elif len(self.terms) == 1:
            return msexp(self, self.terms)

        # Terms with primitve arguments 
        # Example: 
        #       (Variable 'zeta')
        else:
            return sexp(self.classname, *self.args)

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

    def __repr__(self):
         return self.get_math()

    #############################################################

    def set_side(self, side):
        for term in self.terms:
            term.side = side
            term.set_side(side)

    def wrap(self,other):
        '''Take one object and wrap it in container object, return
        the resulting container'''
        return other(self)

    def ensure_id(self):
        '''Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one'''

        if not self.id:
            self.id = self.idgen.next()

    def map_recursive(self,f):
        '''Apply a function to self and all subterms'''
        for term in self.terms:
            term.map_recursive(f)
        f(self)
        return self

