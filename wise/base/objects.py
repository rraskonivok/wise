# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# Import the base term class, that all non-relational terms inherit from
from wise.base.cell import Cell
from wise.base.term import Term

from math import modf

from wise.worksheet.utils import render_haml_to_response
from wise.translators.pure_wrap import PureSymbol, PureInt, PureDouble, ProtoRule, p2i, i2p

import worksheet.exceptions as exception
from worksheet.utils import *

from django import template

class Placeholder(Term):
    '''A placeholder for substitution'''

    css_class = 'placeholder'
    html = load_haml_template('placeholder.tpl')
    pure = 'ph'

    def __init__(self):
        self.latex = '$\\text{Placeholder}$'

    def _pure_(self):

        # If there is a placeholder left in an expression throw
        # an error and abort the pure translation.
        raise exception.PlaceholderInExpression()

    def get_math(self):
        return '(Placeholder )'

class Empty(Term):
    def __init__(self):
        self.latex = '$\\text{Empty}$'

    def get_math(self):
        return 'Empty'

    def combine(self,other,context):
        return other.get_html()

#-------------------------------------------------------------
# Lower Level Elements 
#-------------------------------------------------------------

class Tuple(Term):
    show_parenthesis = True
    html = load_haml_template('tuple.tpl')
    symbol = ','
    pure = 'Tuple'

    def __init__(self, x, *xs):
        self.terms = [x] + list(xs)

    def _pure_(self):
        return self.po(*purify(self.terms))

    def get_html(self):
        objects = [o.get_html() for o in self.terms]

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'operand': objects,
            'symbol': self.symbol,
            'parenthesis': self.show_parenthesis,
            'class': self.css_class,
            })

        return self.html.render(c)

class Text(Term):
    type = 'text'

    def __init__(self,text):
        self.latex = '\\text{' + text + '}'

class PureBlob(Term):
    html = load_haml_template('pureblob.tpl')
    def __init__(self):
        pass

    def get_html(self):
        c = template.Context({'annotation': self.annotation})
        return self.html.render(c)

class Tex(object):
    '''LaTeX sugar for operators'''
    tex = None
    html = load_haml_template('tex.tpl')

    def __init__(self,tex):
        self.tex = tex

    def get_html(self):
        c = template.Context({
            'group': self.group,
            'type': 'Tex',
            'tex': self.tex})

        return self.html.render(c)

greek_alphabet = {
        'alpha'  :  '\\alpha',
        'beta'   :  '\\beta',
        'gamma'  :  '\\gamma',
        'delta'  :  '\\delta',
        'epsilon' :  '\\epsilon',
        'varepsilon' :  '\\varepsilon',
        'zeta'   :  '\\zeta',
        'eta'    :  '\\eta',
        'theta'  :  '\\theta',
        'vartheta' :'\\vartheta',
        'gamma'  :  '\\gamma',
        'kappa'  :  '\\kappa',
        'lambda' :  '\\lambda',
        'mu'     :  '\\mu',
        'nu'     :  '\\nu',
        'xi'     :  '\\xi',
        'pi'     :  '\\pi',
        'varpi'  :  '\\varpi',
        'rho'    :  '\\rho',
        'varrho' :  '\\varrho',
        'sigma'  :  '\\sigma',
        'varsigma' :'\\varsigma',
        'tau'    :  '\\tau',
        'upsilon':  '\\upsilon',
        'phi'    :  '\\phi',
        'varphi' :  '\\varphi',
        'chi'    :  '\\chi',
        'psi'    :  '\\psi',
        'omega'  :  '\\omega',
        'Gamma'  :  '\\Gamma' ,
        'Delta'  :  '\\Delta' ,
        'Theta'  :  '\\Theta' ,
        'Lambda' :  '\\Lambda',
        'Xi'     :  '\\Xi'    ,
        'Pi'     :  '\\Pi'    ,
        'Sigma'  :  '\\Sigma' ,
        'Upsilon':  '\\Upsilon',
        'Phi'    :  '\\Phi'   ,
        'Psi'    :  '\\Psi'   ,
        'Omega'  :  '\\Omega' ,
        }

def greek_lookup(s):
    try:
        return greek_alphabet[s]
    except KeyError:
        return s

class Base_Symbol(Term):

    def __init__(self,*args):
        pass

    def _pure_(self):
        return self.po()

# Conviencence wrapper
def Greek(symbol):
    return Variable(symbol)

class Variable(Base_Symbol):
    '''A free variable'''

    assumptions = None
    bounds = None
    pure = 'var'

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '%s' % greek_lookup(symbol)
        self.args = str(symbol)

    def _pure_(self):
        return PureSymbol(self.symbol)

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
            return PureSymbol(self.symbol + '@_')(PureSymbol('u'))
        #RHS
        else:
            return PureSymbol(self.symbol)(PureSymbol('u'))

class Rational(Term):
    html = load_haml_template('rational.tpl')
    pure = 'rational'

    def __init__(self,num,den):
        self.num = num
        self.den = den
        self.den.css_class = 'middle'
        self.terms = [num,den]

    def _pure_(self):
       return self.po(self.num._pure_(), self.den._pure_())

    def get_html(self):
        self.num.group = self.id
        self.den.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'num': self.num.get_html(),
            'den': self.den.get_html(),
            'group': self.group,
            'type': self.classname,
            'class': self.css_class
            })

        return self.html.render(c)

class Infinity(Base_Symbol):
    latex = '\\infty'
    symbol = 'inf'
    pure = 'inf'
    args = "'inf'"

class Numeric(Term):
    numeric_type = 'float'

    def __init__(self,number):

        self.number = float(number)

        if self.number == 1.0:
            self.number = 1

        fpart, ipart = modf(self.number)

        if fpart == 0:
            self.numeric_type = 'int'
        else:
            self.numeric_type = 'float'

        self.args = number
        self.latex = number

    def _pure_(self):
        if self.numeric_type is 'float':
            return PureDouble(self.number)
        else:
            return PureInt(self.number)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
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
                result = other.get_html()
                return result,[self,other]
            elif isinstance(other,Numeric):
                result = Numeric(self.number + other.number).get_html()
                return result,[self,other]

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

class ComplexNumeric(Term):
    html = load_haml_template('complex.tpl')
    pure = 'complex'

    def __init__(self, re, im):
        self.re = re
        self.im = im
        self.terms = [self.re, self.im]

    def get_html(self):
        self.associate_terms()

        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            're': self.re.get_html(),
            'im': self.im.get_html(),
        })

        return self.html.render(c)

    def _pure_(self):
        return self.po(*purify(self.terms))

#Constants should be able to be represented by multiple symbols
class Constant(Term):
    representation = None

    def __init__(self,*symbol):
        self.args = self.representation.args
        self.latex = self.representation.latex

def Zero():
    return Numeric(0)

def One():
    return Numeric(1)

class ImaginaryUnit(Base_Symbol):
    latex = 'i'
    symbol = 'i'
    pure = 'I'
    args = "'i'"

class Pi(Base_Symbol):
    latex = '\pi'
    symbol = '\pi'
    pure = 'Pi'
    args = '\pi'

#-------------------------------------------------------------
# Top Level Elements
#-------------------------------------------------------------

class Relational(object):
    '''A statement relating some LHS to RHS'''
    pass

class Equation(object):
    html = load_haml_template('equation.tpl')

    lhs = None
    rhs = None
    id = None

    symbol = "="

    sortable = False
    parent = None

    side = None
    annotation = ''

    pure = 'eq'

    po = None

    # Database index
    sid = None

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

        self.terms = [self.lhs, self.rhs]

    def get_math(self):
        return '(' + self.classname + ' ' + spaceiter(map(lambda o: o.get_math(), self.terms)) + ')'

    @property
    def math(self):
        l1 =' '.join([self.classname, self.lhs.get_math(), self.rhs.get_math()])
        return ''.join(['(',l1,')'])

    def __repr__(self):
         return self.math

    def _pure_(self):
        return self.po(self.lhs._pure_(),self.rhs._pure_())

    @property
    def classname(self):
        return self.__class__.__name__

    def set_side(self, side):
        for term in self.terms:
            term.side = side
            term.set_side(side)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({'id': self.id,
                    'type': self.classname,
                    'toplevel': True,
                    'sid': self.sid,
                    'children': [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def get_html(self):
        self.rhs.id = self.idgen.next()
        self.lhs.id = self.idgen.next()

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

class RHS(Term):
    html = load_haml_template('rhs.tpl')

    def __init__(self,*terms):
        self.rhs = Addition(*terms)
        self.terms = [self.rhs]
#        self.args = [self.rhs]
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

class LHS(Term):
    html = load_haml_template('lhs.tpl')

    def __init__(self,*terms):
        self.lhs = Addition(*terms)
        self.terms = [self.lhs]
#        self.args = [self.lhs]
        self.side = 0
        self.lhs.side = 0
        self.lhs.parent = self

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

class Definition(Equation):
    symbol = ":="
    sortable = False
    html = load_haml_template('def.tpl')
    confluent = True
    public = True
    pure = None

    def _pure_(self):
        lhs = self.lhs._pure_()
        rhs = self.rhs._pure_()

        return ProtoRule(lhs , rhs)

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
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'confluent': int(self.confluent),
            'public': self.public,
            'classname': self.classname
            })

        return self.html.render(c)

class Function(Equation):
    symbol = "\\rightarrow"
    sortable = False
    html = load_haml_template('function.tpl')
    confluent = True
    public = True
    pure = None

    def __init__(self,head=None,lhs=None,rhs=None):

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

        self.head = head
        self.lhs = lhs
        self.rhs = rhs

        self.terms = [self.head, self.lhs, self.rhs]

    def _pure_(self):
        lhs = self.lhs._pure_()
        rhs = self.rhs._pure_()

        return ProtoRule(lhs , rhs)

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'math': self.math,
            'head': self.head.get_html(),
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'classname': self.classname
            })

        return self.html.render(c)

#-------------------------------------------------------------
# Operations
#-------------------------------------------------------------

infix_symbol_template = haml('''
.ui-state-disabled.infix.term math-type="infix" math-meta-class="sugar"
    $${{%s}}$$
''')

def infix_symbol_html(symbol):
    return infix_symbol_template % symbol

class Operation(Term):
    '''An operator acting a term'''

    ui_style = 'prefix'

    symbol = None
    show_parenthesis = False
    sortable = False

    #Arity of the operator
    arity = None

    is_linear = False
    is_associative = False

    pure = None

    def __init__(self,op,*ops):
        operands = list(ops) + [op]
        if len(operands) > 1:
            self.terms = list(operands)
            self.operand = self.terms
        else:
            self.operand = operands[0]
            self.terms = [operands[0]]

    def _pure_(self):
        if self.po:
            return self.po(*purify(self.terms))
        else:
            raise exception.PureError('No pure representation of %s.' % self.classname)

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
            self.html = load_haml_template('infix.tpl')
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
                'class': self.css_class,
                })

            return self.html.render(c)

        #Outfix Formatting
        elif self.ui_style == 'outfix':
            self.html = load_haml_template('outfix.tpl')

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
            #self.html = load_haml_template('prefix.tpl')

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
                'class': self.css_class,
                })

        #Postfix Formatting
        elif self.ui_style == 'postfix':
            self.html = load_haml_template('postfix.tpl')

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
            self.html = load_haml_template('sup.tpl')

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
            self.html = load_haml_template('sub.tpl')

            if not self.css_class:
                self.css_class = 'middle'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1,
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Latex Styled Formatting
        elif self.ui_style == 'latex':
            self.html = load_haml_template('latex.tpl')

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
            print('Unknown operator class, should be (infix,postfix,prefix,outfix,sup,sub,latex)')

        return self.html.render(c)

    def get_symbol(self):
        return self.symbol

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        return obj

    def has_single_term(self):
        if len(self.terms) == 1:
            return True

class PrefixOperation(Operation):
    html = load_haml_template('prefix.tpl')
    ui_style = 'prefix'
    show_parenthesis = True

class InfixOperation(Operation):
    ui_style = 'infix'

class PostfixOperation(Operation):
    ui_style = 'postfix'

class PostfixOperation(Operation):
    ui_style = 'postfix'

class SupOperation(Operation):
    ui_style = 'sup'

class SubOperation(Operation):
    ui_style = 'sub'

class OutfixOperation(Operation):
    ui_style = 'outfix'

class Addition(InfixOperation):
    symbol = '+'
    show_parenthesis = False
    pure = 'add'

    def __init__(self,fst,snd=None):
        if snd:
            terms = [fst, snd]
        else:
            terms = [fst]

        self.terms = list(terms)

        #If we have nested Additions collapse them Ex: 
        #(Addition (Addition x y ) ) = (Addition x y)
        if len(terms) == 1:
            if type(terms[0]) is Addition:
                self.terms = terms[0].terms

        self.operand = self.terms
        #js.make_sortable(self)

    def _pure_(self):
        # There is some ambiguity here since we often use an
        # addition operator of arity=1 to make UI magic happen
        # clientside, but we just eliminiate it when converting
        # into a expression
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return self.po(*pterms)

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

class Product(InfixOperation):
    ui_style = 'infix'
    symbol = '\\cdot'
    show_parenthesis = False
    pure = 'mul'

    def __init__(self,fst,snd=None):
        if snd:
            terms = [fst, snd]
        else:
            terms = [fst]

        self.terms = list(terms)

        for term in self.terms:
            term.group = self.id
            if type(term) is Addition:
                term.show_parenthesis = True
        self.operand = self.terms
        #make_sortable(self)
        #self.ui_sortable()

    def remove(self,obj,remove_context):
        if type(self.terms[0]) is Empty:
            return One()

    def _pure_(self):
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return self.po(*pterms)

class Root(Operation):
    html = load_haml_template('power.tpl')
    pure = 'root'

    def __init__(self,base,exponent):
        self.base = base
        self.exponent = exponent
        self.terms = [self.base, self.exponent]
        basetype = type(self.base)
        if basetype is Rational or isinstance(self.base, Rational):
            self.base.show_parenthesis = True
        #make_sortable(self)

    def _pure_(self):
        return self.po(self.base._pure_() , self.exponent._pure_())

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

class Power(Operation):
    html = load_haml_template('power.tpl')
    pure = 'powr'

    def __init__(self,base,exponent):
        self.base = base
        self.exponent = exponent
        self.terms = [self.base, self.exponent]
        basetype = type(self.base)
        if basetype is Rational or isinstance(self.base, Rational):
            self.base.show_parenthesis = True
        #make_sortable(self)

    def _pure_(self):
        return self.po(self.base._pure_() , self.exponent._pure_())

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
            'exponent': self.exponent.get_html()
        })

        return self.html.render(c)

class Interval(InfixOperation):
    html = load_haml_template('power.tpl')


class Sqrt(PrefixOperation):
    html = load_haml_template('root.tpl')

    pure = 'Sqrt'

    def __init__(self,op,*ops):
        operands = list(ops) + [op]
        if len(operands) > 1:
            self.terms = list(operands)
            self.operand = self.terms
        else:
            self.operand = operands[0]
            self.terms = [operands[0]]

        op.css_class = 'sqrt-stem'

#class Abs(OutfixOperation):
#    symbol1 = '|'
#    symbol2 = '|'

class Sgn(PrefixOperation):
    symbol = '\\text{sgn}'

class DiracDelta(PrefixOperation):
    symbol = '\\delta'

class Sin(PrefixOperation):
    symbol = '\\sin'
    pure = 'Sin'

class Cos(PrefixOperation):
    symbol = '\\cos'
    pure = 'Cos'

class Tan(PrefixOperation):
    symbol = '\\tan'
    pure = 'Tan'

class Exp(PrefixOperation):
    symbol = '\\exp'

class Ln(PrefixOperation):
    symbol = '\\ln'
    pure = 'ln'

class Asin(PrefixOperation):
    symbol = '\\sin^{-1}'
    pure = 'asin'

class Acos(PrefixOperation):
    symbol = '\\cos^{-1}'

class Atan(PrefixOperation):
    symbol = '\\tan^{-1}'

class Sinh(PrefixOperation):
    symbol = '\\sinh'
    pure = 'Sinh'

class Cosh(PrefixOperation):
    symbol = '\\cosh'
    pure = 'Cosh'

class Tanh(PrefixOperation):
    symbol = '\\tanh'
    pure = 'Tanh'

class Asinh(PrefixOperation):
    symbol = '\\sinh^{-1}'
    pure = 'Asinh'

class Acosh(PrefixOperation):
    symbol = '\\cosh^{-1}'
    pure = 'Acosh'

class Atanh(PrefixOperation):
    symbol = '\\tanh^{-1}'
    pure = 'Atanh'

class Gamma(PrefixOperation):
    symbol = '\\Gamma'
    pure = 'GammaF'

class Zeta(PrefixOperation):
    symbol = '\\zeta'
    pure = 'RiemannZeta'

class Factorial(PostfixOperation):
    symbol = '!'
    pure = 'Factorial'

class Catalan(SubOperation):
    latex = 'C'
    symbol1 = 'C'
    pure = 'catalan'
    args = "'n'"

class Negate(PrefixOperation):
    symbol = '-'
    show_parenthesis = False
    css_class = 'negate'

    # Capitalize since "neg" already exists in the default Pure
    # predule.
    pure = 'Neg'

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

        if type(self.operand) is Addition:
            self.show_parenthesis = True

    def _pure_(self):
       return self.po(self.operand._pure_())

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        ''' -A+-B = -(A+B)'''

        if context == 'Addition':
            if isinstance(other,Negate):
                return Negate(Addition(self.operand, other.operand))

    def negate(self):
        return self.operand

class FunctionAppl(PrefixOperation):

    def __init__(self, func, args):
        # the math spit out by func get_math is not well-formed
        self.terms = [func, args]
        self.symbol = func.head.symbol
        self.operand = args

class Quote(PrefixOperation):
    symbol = '!'
    pure = 'quote'
