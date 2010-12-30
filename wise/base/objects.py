# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from math import modf

# Subpackages
# -----------
# * cell.py
# * term.py
# * toplevel.py
# * operations.py

from wise.base.cell import Cell
from wise.base.term import Term, Placeholder, ph
from wise.base.toplevel import Relation, EquationPrototype
from wise.base.operations import PrefixOperation, InfixOperation, \
PostfixOperation, SupOperation, SubOperation, OutfixOperation, \
Operation

from wise.worksheet.utils import render_haml_to_response

import worksheet.exceptions as exception

from utils import latex
from worksheet.utils import *

from django import template

__all__ = ['cell', 'term', 'toplevel', 'operations']

def initialize():
    super_classes = [Term, Relation]

    nullary_types = {'num' : Numeric,
                    'var' : Variable,
                    'ph' : Placeholder,
                    '-'   : Negate}

    return super_classes, nullary_types

#-------------------------------------------------------------
# Non-mathematical Symbols
#-------------------------------------------------------------

class Quote(PrefixOperation):
    symbol = '!'
    pure = 'quote'

#class Text(Term):
#    type = 'text'
#
#    def __init__(self,text):
#        self.latex = '\\text{' + text + '}'

#-------------------------------------------------------------
# Nullary / Symbol Type Objects
#-------------------------------------------------------------

class BaseSymbol(Term):
    def __init__(self,*args):
        raise Exception('Naked symbol invoked.')

class Variable(BaseSymbol):
    '''A free variable'''
    pure = 'var'

    def __init__(self,symbol):
        if symbol in latex.greek_unicode:
            self.latex = latex.greek_lookup(symbol)
            self.html = load_haml_template('constant.tpl')
        else:
            self.latex = symbol

        self.symbol = symbol
        self.args = [str(symbol)]

    def _pure_(self):
        from wise.translators.pure_wrap import PureSymbol
        return PureSymbol(self.symbol)

    def _openmath_(self):
        return self.symbol

class Numeric(Term):
    numeric_type = 'float'

    def __init__(self, number):
        self.number = float(number)

        fpart, ipart = modf(self.number)

        if fpart == 0:
            self.numeric_type = 'int'
        else:
            self.numeric_type = 'float'

        self.args = number
        self.latex = number

    def _pure_(self):
        from wise.translators.pure_wrap import PureInt, PureDouble
        if self.numeric_type is 'float':
            return PureDouble(self.number)
        else:
            return PureInt(self.number)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'latex':self.latex,
            'type': self.classname,
        })

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

#-------------------------------------------------------------
# Complex Operations
#-------------------------------------------------------------

class Complex(Term):
    '''General complex quantity.'''
    pass

class ComplexCartesian(Complex):
    '''
    This symbol represents a constructor function for complex numbers
    specified as the Cartesian coordinates of the relevant point on the
    complex plane. It takes two arguments, the first is a number x to
    denote the real part and the second a number y to denote the imaginary
    part of the complex number x + i y. (Where i is the square root of -1.)
    '''
    html = load_haml_template('complex.tpl')
    pure = 'complex'

    cd = 'complex1'
    cd_name = 'complex_cartesian'

    def __init__(self, re, im):
        self.re = re
        self.im = im
        self.terms = [self.re, self.im]

    def get_html(self):

        c = template.Context({
            'id': self.id,
            're': self.re.get_html(),
            'im': self.im.get_html(),
        })

        return self.html.render(c)

    def _pure_(self):
        return self.po(*purify(self.terms))

class ComplexPolar(Complex):
    '''
    This symbol represents a constructor function for complex numbers
    specified as the polar coordinates of the relevant point on the complex
    plane. It takes two arguments, the first is a nonnegative number r to
    denote the magnitude and the second a number theta (given in radians)
    to denote the argument of the complex number r e^(i
    theta).
    '''

    html = load_haml_template('complex.tpl')
    pure = 'complex'

    cd = 'complex1'
    cd_name = 'complex_cartesian'

    def __init__(self, re, im):
        self.re = re
        self.im = im
        self.terms = [self.re, self.im]

    def get_html(self):

        c = template.Context({
            'id': self.id,
            're': self.re.get_html(),
            'im': self.im.get_html(),
        })

        return self.html.render(c)

    def _pure_(self):
        return self.po(*purify(self.terms))

class Real(PrefixOperation):
    pure = 'real'

    cd = 'complex1'
    cd_name = 'real'

class Imaginary(PrefixOperation):
    pure = 'imag'

    cd = 'complex1'
    cd_name = 'imaginary'

class Argument(PrefixOperation):
    pure = 'argm'

    cd = 'complex1'
    cd_name = 'argument'

class Conjugate(PrefixOperation):
    pure = 'conj'

    cd = 'complex1'
    cd_name = 'conjugate'

#-------------------------------------------------------------
# Numerical Constants
#-------------------------------------------------------------

class Constant(Term):
    #Constants should be able to be represented by multiple symbols
    representation = None
    html = load_haml_template('constant.tpl')

#    def __init__(self,*symbol):
#        self.args = self.representation.args
#        self.latex = self.representation.latex

class ImaginaryUnit(Constant):
    '''This symbol represents the square root of -1.'''

    latex = 'i'
    symbol = 'ⅈ'
    pure = 'I'
    args = "'i'"

class Pi(Constant):
    latex = 'π'
    symbol = 'π'
    pure = 'Pi'
    args = "'pi'"

class Infinity(Constant):
    latex = '\\infty'
    symbol = 'inf'
    pure = 'inf'
    args = "'inf'"

#-------------------------------------------------------------
# Algebraic Quantities
#-------------------------------------------------------------

def Zero(Constant):
    '''This symbol represents the additive identity element.'''
    cd = 'alg1'
    cd_name = 'zero'

    latex = '0'
    symbol = '0'
    pure = 'zero'


def One(Constant):
    '''This symbol represents the multiplicative identity element.'''

    cd = 'alg1'
    cd_name = 'one'

    latex = '1'
    symbol = '1'
    pure = 'one'

#-------------------------------------------------------------
# Integer Functions
#-------------------------------------------------------------

class Quotient(PrefixOperation):
    symbol = 'quotient'
    pure = 'quo'

    cd = 'integer1'
    cd_name = 'quotient'

class Remainder(PrefixOperation):
    symbol = 'remainder'
    pure = 'rem'

    cd = 'integer1'
    cd_name = 'remainder'

class Factorial(PostfixOperation):
    symbol = '!'
    pure = 'fact'

    cd = 'integer1'
    cd_name = 'factorial'

class Catalan(SubOperation):
    latex = 'C'
    symbol1 = 'C'
    pure = 'catalan'
    args = "'n'"

#-------------------------------------------------------------
# Arithmetic Functions
#-------------------------------------------------------------

class LCM(PrefixOperation):
    symbol = '\\lcm'
    pure = 'lcm'

    cd = 'arith1'
    cd_name = 'lcm'

class GCD(PrefixOperation):
    symbol = '\\gcd'
    pure = 'gcd'

    cd = 'arith1'
    cd_name = 'gcd'

class Addition(InfixOperation):
    symbol = '+'
    show_parenthesis = False
    pure = 'add'

    cd = 'arith1'
    cd_name = 'plus'

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
    symbol = '·'
    show_parenthesis = False
    pure = 'mul'

    cd = 'arith1'
    cd_name = 'times'

    def __init__(self,fst,snd=None):
        if snd:
            terms = [fst, snd]
        else:
            terms = [fst]

        self.terms = list(terms)

        #for term in self.terms:
        #    if term.terms and len(term.terms) > 1:
        #        term.show_parenthesis = True

        self.operand = self.terms

    def remove(self,obj,remove_context):
        if type(self.terms[0]) is Empty:
            return One()

    def _pure_(self):
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return self.po(*pterms)

class NRoot(Operation):
    html = load_haml_template('root.tpl')
    cd = 'arith1'
    cd_name = 'nroot'

    pure = 'NRoot'

    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent
        self.terms = [self.base, self.exponent]

    def _pure_(self):
        return self.po(self.base._pure_() , self.exponent._pure_())

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'base': self.base.get_html(),
            'type': self.classname,
            'exponent': self.exponent.get_html() })

        return self.html.render(c)

class Power(Operation):
    html = load_haml_template('power.tpl')
    pure = 'powr'

    cd = 'arith1'
    cd_name = 'power'

    def __init__(self,base,exponent):
        self.base = base
        self.exponent = exponent
        self.terms = [self.base, self.exponent]
        basetype = type(self.base)

        for term in self.terms:
            if term.terms and len(term.terms) > 1:
                term.show_parenthesis = True

    def _pure_(self):
        return self.po(self.base._pure_() , self.exponent._pure_())

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'base': self.base.get_html(),
            'type': self.classname,
            'exponent': self.exponent.get_html()
        })

        return self.html.render(c)

class Rational(Term):
    html = load_haml_template('rational.tpl')
    pure = 'rational'

    def __init__(self,num,den):
        self.num = num
        self.den = den
        self.terms = [num,den]

    def _pure_(self):
       return self.po(self.num._pure_(), self.den._pure_())

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'num': self.num.get_html(),
            'den': self.den.get_html(),
            'parenthesis': self.show_parenthesis,
            'type': self.classname,
            })

        return self.html.render(c)


class Interval(InfixOperation):
    html = load_haml_template('power.tpl')

class Minus(InfixOperation):
    symbol = '\\cdot'
    show_parenthesis = False
    pure = 'sub'

    cd = 'arith1'
    cd_name = 'minus'

class Negate(PrefixOperation):
    ''' Unary negation'''
    symbol = '-'
    show_parenthesis = False
    css_class = 'negate'

    cd = 'arith1'
    cd_name = 'unary_minus'

    # Capitalize since "neg" already exists in the default Pure
    # predule.
    pure = 'Neg'

    def __init__(self,operand):
        self.operand = operand
        self.terms = [self.operand]

        if type(self.operand) is Addition:
            self.show_parenthesis = True

    def _pure_(self):
       return self.po(self.operand._pure_())

    def negate(self):
        return self.operand

class Sqrt(NRoot):
    html = load_haml_template('sqrt.tpl')
    cd = 'arith1'
    cd_name = 'root'

    pure = 'Sqrt'

    def __init__(self,base):
        self.base = base
        self.exponent = Numeric(2)
        self.terms = [self.base]

    def _pure_(self):
        return self.po(self.base._pure_())

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'base': self.base.get_html(),
            'type': self.classname,
            'exponent': self.exponent.get_html() })

        return self.html.render(c)

class Abs(OutfixOperation):
    symbol1 = '|'
    symbol2 = '|'

    cd = 'arith1'
    cd_name = 'abs'

    pure = 'abs'

class Inverse(SupOperation):
    cd = 'arith2'
    cd_name = 'inverse'

class Sgn(PrefixOperation):
    symbol = '\\text{sgn}'

class DiracDelta(PrefixOperation):
    symbol = '\\delta'

#-------------------------------------------------------------
# Set Theory Functions
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
            'operand': objects,
            'symbol': self.symbol,
            'parenthesis': self.show_parenthesis,
            })

        return self.html.render(c)

class Set(Term):
    show_parenthesis = True
    html = load_haml_template('set.tpl')
    symbol = ','
    pure = 'Set'

    def __init__(self, x, *xs):
        self.terms = [x] + list(xs)

    def _pure_(self):
        return self.po(*purify(self.terms))

    def get_html(self):
        objects = [o.get_html() for o in self.terms]

        c = template.Context({
            'id': self.id,
            'operand': objects,
            'symbol': self.symbol,
            'parenthesis': self.show_parenthesis,
            })

        return self.html.render(c)

class Integral(Term):
    show_parenthesis = True
    html = load_haml_template('integral.tpl')
    pure = 'integrate'

    def __init__(self, f, dx):
        self.integrand = f
        self.variable = dx
        self.terms = [f, dx]

    def _pure_(self):
        return self.po(*purify(self.terms))

    def get_html(self):
        objects = [o.get_html() for o in self.terms]

        c = template.Context({
            'id': self.id,
            'integrand': self.integrand.get_html(),
            'variable': self.variable.get_html(),
            })

        return self.html.render(c)


class CartesianProduct(InfixOperation):
    symbol = '×'
    pure = 'carts'

    cd = 'set1'
    cd_name = 'cartesian_product'

class EmptySet(Term):
    symbol = '∅'
    latex = '\\emptyset'

class Intersect(InfixOperation):
    symbol = '\\cup'
    pure = 'intersect'

    cd = 'set1'
    cd_name = 'intersect'

class Union(InfixOperation):
    symbol = '\\cap'
    pure = 'union'

    cd = 'set1'
    cd_name = 'union'

#-------------------------------------------------------------
# Transcendental Functions
#-------------------------------------------------------------

class Exp(PrefixOperation):
    symbol = 'exp'

class Ln(PrefixOperation):
    symbol = 'ln'
    pure = 'ln'

class Sin(PrefixOperation):
    symbol = 'sin'
    pure = 'Sin'

class Cos(PrefixOperation):
    symbol = 'cos'
    pure = 'Cos'

class Tan(PrefixOperation):
    symbol = 'tan'
    pure = 'Tan'

class Asin(PrefixOperation):
    symbol = 'asin'
    pure = 'Asin'

class Acos(PrefixOperation):
    symbol = 'acos'
    pure = 'Acos'

class Atan(PrefixOperation):
    symbol = 'atan'
    pure = 'Atan'

class Sinh(PrefixOperation):
    symbol = 'sinh'
    pure = 'Sinh'

class Cosh(PrefixOperation):
    symbol = 'cosh'
    pure = 'Cosh'

class Tanh(PrefixOperation):
    symbol = 'tanh'
    pure = 'Tanh'

class Asinh(PrefixOperation):
    symbol = 'asinh'
    pure = 'Asinh'

class Acosh(PrefixOperation):
    symbol = 'acosh'
    pure = 'Acosh'

class Atanh(PrefixOperation):
    symbol = 'atanh'
    pure = 'Atanh'

class Gamma(PrefixOperation):
    symbol = 'Γ'
    pure = 'GammaF'

class Zeta(PrefixOperation):
    symbol = 'ζ'
    pure = 'RiemannZeta'

#-------------------------------------------------------------
# Generalized Functions
#-------------------------------------------------------------

class FunctionAppl(PrefixOperation):

    def __init__(self, func, args):
        # the math spit out by func get_math is not well-formed
        self.terms = [func, args]
        self.symbol = func.head.symbol
        self.operand = args

#Free abstract function (of a single variable at this time)
class FreeFunction(BaseSymbol):

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s(u)$' % symbol
        self.args = str(symbol)

    def _pure_(self):
        from wise.translators.pure_wrap import PureSymbol

        #LHS
        if self.side is 0:
            return PureSymbol(self.symbol + '@_')(PureSymbol('u'))
        #RHS
        else:
            return PureSymbol(self.symbol)(PureSymbol('u'))

#-------------------------------------------------------------
# Assumptions
#-------------------------------------------------------------

class Assumption(PrefixOperation):
    html = load_haml_template('assumption.tpl')
    symbol = '?'
    pure = 'assum'
    toplevel = True

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({'id': self.id,
                    'type': self.classname,
                    'toplevel': self.toplevel,
                    'sid': self.sid,
                    'children': [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

class AssumptionPrototype(Assumption):
    pure = None

    def __init__(self):
        Assumption.__init__(self, ph())

    @property
    def classname(self):
        return 'Assumption'

#vim: ai ts=4 sts=4 et sw=4
