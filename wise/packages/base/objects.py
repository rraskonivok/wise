# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
from math import modf

from operations import (PrefixOperation, InfixOperation,
PostfixOperation, SupOperation, SubOperation, OutfixOperation,
Operation)
from term import Term, Placeholder
from toplevel import Relation

from wise.translators import pureobjects
from wise.worksheet.utils import *
from wise.utils import latex
from django import template

# Subpackages
# -----------
# * cell.py
# * term.py
# * toplevel.py
# * operations.py

def initialize():
    super_classes = [Term, Relation]

    nullary_types = {
        'num' : Numeric,
        'var' : Variable,
        'ph' : Placeholder,
    }

    return super_classes, nullary_types

#-------------------------------------------------------------
# Nullary / Symbol Type Objects
#-------------------------------------------------------------

class Variable(Term):
    """
    A free variable
    """
    pure = 'var'

    def __init__(self,symbol):

        if is_number(symbol):
            raise TypeError(symbol)

        if symbol in latex.greek_unicode:
            self.latex = latex.greek_lookup(symbol)
            self.html = load_haml_template('constant.tpl')
        else:
            self.latex = symbol

        self.symbol = symbol
        self.args = [str(symbol)]

    def _pure_(self):
        return pureobjects.PureSymbol(self.symbol)

    def _openmath_(self):
        return self.symbol

class Numeric(Term):
    numeric_type = 'float'

    def __init__(self, number):

        if not is_number(number):
            raise TypeError(number)

        self.number = float(number)
        fpart, ipart = modf(self.number)

        if fpart == 0:
            self.numeric_type = 'int'
        else:
            self.numeric_type = 'float'

        self.args = number
        self.latex = number

    def _pure_(self):
        if self.numeric_type is 'float':
            return pureobjects.PureDouble(self.number)
        else:
            return pureobjects.PureInt(self.number)

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

#-------------------------------------------------------------
# Complex Operations
#-------------------------------------------------------------

class Complex(Term):
    """
    General complex quantity.
    """
    pass

class ComplexCartesian(Complex):
    """
    This symbol represents a constructor function for complex numbers
    specified as the Cartesian coordinates of the relevant point on the
    complex plane. It takes two arguments, the first is a number x to
    denote the real part and the second a number y to denote the imaginary
    part of the complex number x + i y. (Where i is the square root of -1.)
    """
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
        return self.po(self.re._pure_(),self.im._pure_())

class ComplexPolar(Complex):
    """
    This symbol represents a constructor function for complex numbers
    specified as the polar coordinates of the relevant point on the complex
    plane. It takes two arguments, the first is a nonnegative number r to
    denote the magnitude and the second a number theta (given in radians)
    to denote the argument of the complex number r e^(i
    theta).
    """

    html = load_haml_template('complex.tpl')
    pure = 'complex_polar'

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
    """
    This represents the real part of a complex number
    """
    pure = 'real'

    cd = 'complex1'
    cd_name = 'real'

class Imaginary(PrefixOperation):
    """
    This represents the imaginary part of a complex number
    """

    pure = 'imag'

    cd = 'complex1'
    cd_name = 'imaginary'

class Argument(PrefixOperation):
    """
    This symbol represents the unary function which returns the
    argument of a complex number.
    """
    pure = 'argm'

    cd = 'complex1'
    cd_name = 'argument'

class Conjugate(PrefixOperation):
    """
    A unary operator representing the complex conjugate of its argument.
    """

    pure = 'conj'

    cd = 'complex1'
    cd_name = 'conjugate'

#-------------------------------------------------------------
# Numerical Constants
#-------------------------------------------------------------

class Constant(Term):
    """
    A symbol to be used as the argument of the type symbol to
    convey a type for the common constants.
    """

    #Constants should be able to be represented by multiple symbols
    representation = None
    html = load_haml_template('constant.tpl')

#    def __init__(self,*symbol):
#        self.args = self.representation.args
#        self.latex = self.representation.latex

class ImaginaryUnit(Constant):
    """
    This symbol represents the square root of -1.
    """

    latex = 'i'
    symbol = 'ⅈ'
    pure = 'I'
    args = "'i'"

class Pi(Constant):
    """
    A symbol to convey the notion of pi, approximately 3.142. The
    ratio of the circumference of a circle to its diameter.
    """

    latex = 'π'
    symbol = 'π'
    pure = 'Pi'
    args = "'pi'"

class Infinity(Constant):
    """
    A symbol to represent the notion of infinity.
    """

    latex = '\\infty'
    symbol = 'inf'
    pure = 'inf'
    args = "'inf'"

#-------------------------------------------------------------
# Algebraic Quantities
#-------------------------------------------------------------

def Zero(Constant):
    """
    This symbol represents the additive identity element.
    """
    cd = 'alg1'
    cd_name = 'zero'

    latex = '0'
    symbol = '0'
    pure = 'zero'


def One(Constant):
    """
    This symbol represents the multiplicative identity element.
    """

    cd = 'alg1'
    cd_name = 'one'

    latex = '1'
    symbol = '1'
    pure = 'one'

#-------------------------------------------------------------
# Integer Functions
#-------------------------------------------------------------

class Quotient(PrefixOperation):
    """
    The symbol to represent the integer (binary) division
    operator. That is, for integers a and b, quotient(a,b)
    denotes q such that a=b*q+r, with |r| less than |b| and a*r
    positive.
    """
    symbol = 'quotient'
    pure = 'quo'

    cd = 'integer1'
    cd_name = 'quotient'

class Remainder(PrefixOperation):
    """
    The symbol to represent the integer remainder after (binary)
    division. For integers a and b, remainder(a,b) denotes r such
    that a=b*q+r, with |r| less than |b| and a*r positive.
    """

    symbol = 'remainder'
    pure = 'rem'

    cd = 'integer1'
    cd_name = 'remainder'

class Factorial(PostfixOperation):
    """
    The symbol to represent a unary factorial function on
    non-negative integers.
    """

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
    """
    The symbol to represent the n-ary function to return the
    least common multiple of its arguments.
    """

    symbol = '\\lcm'
    pure = 'lcm'

    cd = 'arith1'
    cd_name = 'lcm'

class GCD(PrefixOperation):
    """
    The symbol to represent the n-ary function to return the gcd
    (greatest common divisor) of its arguments.
    """

    symbol = '\\gcd'
    pure = 'gcd'

    cd = 'arith1'
    cd_name = 'gcd'

class Addition(InfixOperation):
    """
    The symbol representing an binary commutative function plus.
    """

    symbol = '+'
    show_parenthesis = False
    pure = 'add'

    cd = 'arith1'
    cd_name = 'plus'

    def __init__(self,fst, snd):
        self.terms = [fst, snd]
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

class Product(InfixOperation):
    """
    The symbol representing an binary multiplication function.
    """

    symbol = '·'
    show_parenthesis = False
    pure = 'mul'

    cd = 'arith1'
    cd_name = 'times'

    def __init__(self,fst,snd):
        self.terms = [fst, snd]

        for term in self.terms:
            if term.terms and len(term.terms) > 1:
                term.show_parenthesis = True

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
    """
    A binary operator which represents its first argument
    "lowered" to its n'th root where n is the second argument.
    """

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
    """
    This symbol represents a power function. The first argument is
    raised to the power of the second argument. When the second
    argument is not an integer, powering is defined in terms of
    exponentials and logarithms for the complex and real numbers.
    """

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

        if isinstance(base,Rational):
            self.base.show_parenthesis = True

    def _pure_(self):
        return self.po(self.base._pure_() , self.exponent._pure_())

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'base': self.base.get_html(),
            'type': self.classname,
            'exponent': self.exponent.get_html(),
            'parenthesis':self.show_parenthesis,
        })

        return self.html.render(c)

class Rational(Term):
    """
    This symbol represents the constructor function for rational
    numbers. It takes two arguments, the first is an integer p to
    denote the numerator and the second a nonzero integer q to
    denote the denominator of the rational p/q.
    """

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
    """
    A symbol to denote a continuous 1-dimensional interval
    without any information about the character of the end points
    (used in definite integration). The arguments are the start
    and the end points of the interval in that order.
    """

    html = load_haml_template('power.tpl')

class Minus(InfixOperation):
    """
    The symbol representing a binary minus function. This is
    equivalent to adding the additive inverse.
    """

    symbol = '\\cdot'
    show_parenthesis = False
    pure = 'sub'

    cd = 'arith1'
    cd_name = 'minus'

class Negate(PrefixOperation):
    """
    The symbol representing a unary negate function.
    """

    symbol = '-'
    show_parenthesis = False
    css_class = 'negate'

    cd = 'arith1'
    cd_name = 'unary_minus'

    # Capitalized since "neg" already exists in the default Pure
    # predule and we can't overload it :-(
    pure = 'Neg'

    def __init__(self,operand):
        self.operand = operand
        self.terms = [self.operand]

        if type(self.operand) is Addition:
            self.show_parenthesis = True

    def _pure_(self):
       return self.po(self.operand._pure_())

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
    """
    A unary operator which represents the absolute value of its
    argument. The argument should be numerically valued. In the
    complex case this is often referred to as the modulus.
    """

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
    """
    The n-ary tupling constructor when n>2. The arguments are the
    element of the tuple. Tuple objects can also be constructed
    by successive nesting of Pair.
    """

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
    """
    This symbol represents the set construct. It is an n-ary
    function. The set entries are given explicitly. There is no
    implied ordering to the elements of a set.
    """

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


class CartesianProduct(InfixOperation):
    """
    This symbol represents an n-ary construction function for
    constructing the Cartesian product of multisets. It takes n
    multiset arguments in order to construct their Cartesian
    product.
    """

    symbol = '×'
    pure = 'carts'

    cd = 'set1'
    cd_name = 'cartesian_product'

class EmptySet(Term):
    """
    This symbol is used to represent the empty set, that is the set which contains no members. It takes no parameters.
    """

    symbol = '∅'
    latex = '\\emptyset'

class Intersect(InfixOperation):
    """
    This symbol is used to denote the n-ary intersection of sets.
    It takes sets as arguments, and denotes the set that contains
    all the elements that occur in all of them.
    """

    symbol = '\\cup'
    pure = 'intersect'

    cd = 'set1'
    cd_name = 'intersect'

class Union(InfixOperation):
    """
    This symbol is used to denote the n-ary union of sets. It takes
    sets as arguments, and denotes the set that contains all the
    elements that occur in any of them.
    """

    symbol = '\\cap'
    pure = 'union'

    cd = 'set1'
    cd_name = 'union'

#-------------------------------------------------------------
# Transcendental Functions
#-------------------------------------------------------------

class Exp(PrefixOperation):
    """
    This symbol represents the exponentiation function.
    """
    symbol = 'exp'

class Ln(PrefixOperation):
    """
    This symbol represents the ln function (natural logarithm).
    """
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
class FreeFunction(Term):

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s(u)$' % symbol
        self.args = str(symbol)

    def _pure_(self):

        #LHS
        if self.side is 0:
            return pureobjects.PureSymbol(self.symbol + '@_')(pureobjects.PureSymbol('u'))
        #RHS
        else:
            return pureobjects.PureSymbol(self.symbol)(pureobjects.PureSymbol('u'))

#-------------------------------------------------------------
# Assumptions
#-------------------------------------------------------------

#class Assumption(PrefixOperation):
#    html = load_haml_template('assumption.tpl')
#    symbol = '?'
#    pure = 'assum'
#    toplevel = True
#
#    def json_flat(self,lst=None):
#        if not lst:
#            lst = []
#
#        lst.append({'id': self.id,
#                    'type': self.classname,
#                    'toplevel': self.toplevel,
#                    'sid': self.sid,
#                    'children': [term.id for term in self.terms]})
#
#        for term in self.terms:
#            term.json_flat(lst)
#
#        return lst
#
#class AssumptionPrototype(Assumption):
#    pure = None
#
#    def __init__(self):
#        Assumption.__init__(self, ph())
#
#    @property
#    def classname(self):
#        return 'Assumption'

#-------------------------------------------------------------
# Non-mathematical Symbols
#-------------------------------------------------------------

class Quote(PrefixOperation):
    symbol = '!'
    pure = 'quote'

#vim: ai ts=4 sts=4 et sw=4
