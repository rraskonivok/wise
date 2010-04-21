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

from wise.worksheet.mathobjects import *
from django.utils import simplejson as json

from wise.worksheet.models import MathematicalTransform
from wise.worksheet.models import MathematicalIdentity

def require(arg_name, *allowed_types):
    def make_wrapper(f):
        if hasattr(f, "wrapped_args"):
            wrapped_args = getattr(f, "wrapped_args")
        else:
            code = f.func_code
            wrapped_args = list(code.co_varnames[:code.co_argcount])

        try:
            arg_index = wrapped_args.index(arg_name)
        except ValueError:
            raise NameError, arg_name

        def wrapper(*args, **kwargs):
            if len(args) > arg_index:
                arg = args[arg_index]
                if not isinstance(arg, allowed_types):
                    type_list = " or ".join(str(allowed_type) for allowed_type in allowed_types)
                    raise TypeError, "Expected '%s' to be %s; was %s." % (arg_name, type_list, type(arg))
            else:
                if arg_name in kwargs:
                    arg = kwargs[arg_name]
                    if not isinstance(arg, allowed_types):
                        type_list = " or ".join(str(allowed_type) for allowed_type in allowed_types)
                        raise TypeError, "Expected '%s' to be %s; was %s." % (arg_name, type_list, type(arg))

            return f(*args, **kwargs)

        wrapper.wrapped_args = wrapped_args
        return wrapper

    return make_wrapper

#@require("x", int, float)
#@require("y", float)
#def foo(x, y):
#    return x+y

# TODO A wrapper to do type checking on these methods and automatically
# provide an error message?

#-------------------------------------------------------------
# Transforms
#-------------------------------------------------------------

class Transform(object):
    first_type = None
    second_type = None
    context = None

#-------------------------------------------------------------
# Replace : (Term, Term) --> Term
#-------------------------------------------------------------

#This should only be used internally by the UI

MathematicalTransform(
        internal='Replace',
        first='',
        second='',
        context = '',
        prettytext = '').save()

class Replace(Transform):
    def __new__(self,first,second):
        return json.dumps({'first': second.get_html()})

#-------------------------------------------------------------
# Placeholder Substitute : (Placeholder, Term) --> Term
#-------------------------------------------------------------

MathematicalTransform(
        internal='PlaceholderSubstitute',
        first='Placeholder',
        second='Term',
        context = 'null',
        prettytext = 'Substitute').save()

class PlaceholderSubstitute(Transform):
    def __new__(self,first,second):
            if type(first) is Placeholder:
                return json.dumps({'first': second.get_html()})
            elif type(second) is Placeholder:
                return json.dumps({'second': first.get_html()})
            else:
                return json.dumps({'error': 'Please select Placeholder object for for first selection'})

#-------------------------------------------------------------
# Term Substitute : (Equation, Term) --> Term
#-------------------------------------------------------------

MathematicalTransform(
        internal='TermSubstitute',
        first='Equation',
        second='Term',
        context = 'null',
        prettytext = 'Substitute').save()

class TermSubstitute(Transform):

    def __new__(self,first,second):

        #If the lhs of the equation matches the variable we are trying to substitue into
        if first.lhs.hash == second.hash:
            second = first.rhs.rhs
            return json.dumps({'second': second.get_html()})
        else:
            return json.dumps({'error': 'Cannot substitute'})

#-------------------------------------------------------------
# DistributeNegation : (Negate, Addition) --> (Negate , ...)
#-------------------------------------------------------------

MathematicalTransform(
        internal='DistributeNegation',
        first='Negate',
        second='Addition',
        context = 'null',
        prettytext = 'Distribute Negation').save()

class DistributeNegation(Transform):

    def __new__(self,first,second):
        distributed = map(Negate,second.terms)
        distributed = map(lambda o: o.get_html(),distributed)
        html = infix_symbol_html(Addition.symbol).join(distributed)

        return json.dumps({'first': html})

#-------------------------------------------------------------
# AdditiveGroup : (Term, Term) --> Addition
#-------------------------------------------------------------

MathematicalTransform(
        internal='AdditiveGroup',
        first='Term',
        second='Term',
        context = 'Addition',
        prettytext = 'Group with Parentheses').save()

class AdditiveGroup(Transform):

    def __new__(self,first,second):

        group = first + second
        group.show_parenthesis = True

        return json.dumps({'first': group.get_html(), 'remove': 'second'})

#-------------------------------------------------------------
# AdditiveSwap : (Term, Term) --> (Term, Term)
#-------------------------------------------------------------

MathematicalTransform(
        internal='AdditiveSwap',
        first='Term',
        second='Term',
        context = 'Addition',
        prettytext = '$$x+y=y+x$$').save()

class AdditiveSwap(Transform):
    def __new__(self,first,second):
        return json.dumps({'first': second.get_html(), 'second': first.get_html()})

#-------------------------------------------------------------
# MultiplicativeSwap : (Term, Term) --> (Term, Term)
#-------------------------------------------------------------

MathematicalTransform(
        internal='MultiplicativeSwap',
        first='Term',
        second='Term',
        context = 'Product',
        prettytext = '$$x \cdot y=y \cdot x$$').save()

class MultiplicativeSwap(Transform):

    def __new__(self,first,second):
        return json.dumps({'first': second.get_html(), 'second': first.get_html()})

#-------------------------------------------------------------
# MultiplicativeSwap : (LHS, RHS) --> (RHS, LHS)
#-------------------------------------------------------------

MathematicalTransform(
        internal='EquationSymmetric',
        first='LHS',
        second='RHS',
        context = 'Equation',
        prettytext = 'Swap Sides of Equation').save()

class EquationSymmetric(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        return json.dumps({'first': second.get_html(), 'second': first.get_html()})

MathematicalTransform(internal='EquationTransitive',
        first='Equation',
        second='Equation',
        context = 'null',
        prettytext = 'Apply Transitive Identity').save()

#-------------------------------------------------------------
# EquationTransitive : (Equation, Equation) --> (Equation)
#-------------------------------------------------------------

class EquationTransitive(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        if first.rhs.hash == second.lhs.hash:
            lhs = first.lhs.lhs
            rhs = second.rhs.rhs
            #TODO: add a 'newline' option to json response
            return json.dumps({'first': lhs.get_html(), 'second': rhs.get_html()})
        else:
            return json.dumps({'error': 'RHS of Equation 1 does not match LHS of Equation 2'})

MathematicalTransform(
        internal='AddNumerics',
        first='Numeric',
        second='Numeric',
        context = 'Addition',
        prettytext = 'Add Numbers').save()

class AddNumerics(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        sumof = Numeric(first.number + second.number)
        return json.dumps({'first': sumof.get_html(), 'second': None})

MathematicalTransform(
        internal='Integrate',
        first='Equation',
        second='Variable',
        context = 'null',
        prettytext = 'Incremental Integral').save()

class Integrate(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        ldifferential = Differential(second)
        rdifferential = Differential(second)
        new_lhs = LHS(Integral(first.lhs.lhs, ldifferential))
        new_rhs = RHS(Integral(first.rhs.rhs, rdifferential))

        new_lhs.lhs.ui_sortable(new_rhs.rhs)
        new_rhs.rhs.ui_sortable(new_lhs.lhs)

        new_eq = Equation(new_lhs, new_rhs)
        return json.dumps({'first': new_eq.get_html()})

MathematicalTransform(
        internal='Differentiate',
        first='LHS',
        second='RHS',
        context = 'Equation',
        prettytext = '$$\\frac{d}{d x} A = \\frac{d}{d x} B$$').save()

class Differentiate(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        try:
            dv = sage.diff(first._sage_())
            first = parse_sage_exp(dv)

            dv = sage.diff(second._sage_())
            second = parse_sage_exp(dv)

            first = LHS(first)
            second = RHS(second)

            first.lhs.ui_sortable(second.rhs)
            second.rhs.ui_sortable(first.lhs)
        except ValueError, e:
            return json.dumps({'error': str(e)})

        return json.dumps({'first': first.get_html(), 'second': second.get_html()})

MathematicalTransform(
        internal='DifferentiateEq',
        first='Equation',
        second='Variable',
        context = 'null',
        prettytext = 'Differentiate').save()

class DifferentiateEq(Transform):
    def __new__(self,first,second):
        try:
            #Differentiate wrt to the specified variable
            dvar = second._sage_()

            #Take the derivative of the LHS and RHS of the equation
            lhs = first.lhs._sage_()
            d = sage.diff(lhs,dvar)
            print 'lhs',lhs,d
            dlhs = parse_sage_exp(d)

            rhs = first.rhs._sage_()
            d = sage.diff(rhs,dvar)
            print 'rhs',lhs,d
            drhs = parse_sage_exp(d)

            first = Equation(LHS(dlhs),RHS(drhs))
        except ValueError, e:
            return json.dumps({'error': str(e)})

        return json.dumps({'first': first.get_html()})

MathematicalTransform(
        internal='IntegrateEq',
        first='Equation',
        second='Variable',
        context = 'null',
        prettytext = 'Integrate').save()

class IntegrateEq(Transform):
    def __new__(self,first,second):
        try:
            #Integrate wrt to the specified variable
            dvar = second._sage_()

            #Take the integral of the LHS and RHS of the equation
            lhs = first.lhs._sage_()
            d = sage.integrate(lhs,dvar)
            dlhs = parse_sage_exp(d)

            rhs = first.rhs._sage_()
            d = sage.integrate(rhs,dvar)
            drhs = parse_sage_exp(d)

            first = Equation(LHS(dlhs),RHS(drhs))
        except ValueError, e:
            return json.dumps({'error': str(e)})

        return json.dumps({'first': first.get_html()})

MathematicalTransform(
        internal='DifferentiateInternal',
        first='Equation',
        second='Variable',
        context = 'null',
        prettytext = 'Incremental Derivative').save()

class DifferentiateInternal(Transform):
    def __new__(self,first,second):
        try:
            dlhs = Diff(second, first.lhs.lhs)
            drhs = Diff(second, first.rhs.rhs)

            first = Equation(LHS(dlhs),RHS(drhs))
        except ValueError, e:
            return json.dumps({'error': str(e)})

        '''
        first = LHS(Diff(first.lhs))
        second = RHS(Diff(second.rhs))

        first.lhs.ui_sortable(second.rhs)
        second.rhs.ui_sortable(first.lhs)
        '''

        return json.dumps({'first': first.get_html()})

MathematicalTransform(
        internal='LinearDistritubeIntegral',
        first='Integral',
        second='Addition',
        context = 'null',
        prettytext = 'Distribute Integral').save()

class LinearDistritubeIntegral(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        print second.terms
        split = [Integral(term,first.differential) for term in second.terms]
        #split = map(Integral,second.terms)
        distributed = Addition(*split)
        return json.dumps({'first': distributed.get_html()})

MathematicalTransform(
        internal='LinearCombineIntegral',
        first='Integral',
        second='Integral',
        context = 'Addition',
        prettytext = 'Combine Integrals').save()

class LinearCombineIntegral(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        combined = Integral(first.operand + second.operand)
        return json.dumps({'first': combined.get_html(), 'remove': 'second'})

MathematicalTransform(
        internal='LinearDistritubeDiff',
        first='Diff',
        second='Addition',
        context = 'null',
        prettytext = 'Propogate Differential through Addition').save()

class LinearDistritubeDiff(Transform):
    first_type = [ Term ]
    second_type = [ Term ]
    context = Addition

    def __new__(self,first,second):
        if first.operand.hash != second.hash:
            return json.dumps({'error': 'Addition term should be not be nested more than one level down'})
        split = [Diff(first.differential, term) for term in second.terms]
        distributed = Addition(*split)
        return json.dumps({'first': distributed.get_html()})

MathematicalTransform(
        internal='DiffLeibniz',
        first='Diff',
        second='Product',
        context = 'null',
        prettytext = 'Propogate Differential through Multiplication').save()

class DiffLeibniz(Transform):
    def __new__(self,first,second):
        if first.operand.hash != second.hash:
            return json.dumps({'error': 'Multiplication term should be not be nested'})

        def leibniz(f,g):
            cross = (Diff(f)*g) + (f*Diff(g))
            cross.show_parenthesis = True
            return cross

        newterms = reduce(leibniz,second.terms)
        newsum = Addition(newterms)
        return json.dumps({'first': newsum.get_html()})

MathematicalTransform(
        internal='DiffNegate',
        first='Diff',
        second='Negate',
        context = 'null',
        prettytext = 'Factor out Negative Sign').save()

class DiffNegate(Transform):
    def __new__(self,first,second):
        if first.operand.hash != second.hash:
            return json.dumps({'error': 'Multiplication term should be not be nested'})

        propogate = Negate( Diff(second.operand) )
        return json.dumps({'first': propogate.get_html()})

MathematicalTransform(
        internal='DiffPropogate',
        first='Diff',
        second='Term',
        context = 'null',
        prettytext = 'Propogate Differential through Expression').save()

class DiffPropogate(Transform):
    def __new__(self,first,second):
        if first.operand.hash != second.hash:
            return json.dumps({'error': 'Term should be not be nested'})

        propogate = first.propogate()
        return json.dumps({'first': propogate.get_html()})

MathematicalTransform(
        internal='DiffMerge',
        first='Addition',
        second='Addition',
        context = 'Addition',
        prettytext = '$$ Propogate $$').save()

class DiffMerge(Transform):
    def __new__(self,first,second):

        merged = Addition(first.terms.extend(second.terms))
        return json.dumps({'first': merged.get_html()})

#-------------------------------------------------------------
# Identities
#-------------------------------------------------------------

class Identity(object):
    first_type = None


MathematicalIdentity(
        internal='RefreshTerm',
        first='Term',
        prettytext = 'Refresh').save()

class RefreshTerm(Identity):
    def __new__(self,first):
        return json.dumps({'first': first.get_html()})


MathematicalIdentity(
        internal='RefreshEq',
        first='Equation',
        prettytext = 'Refresh').save()

class RefreshEq(Identity):
    def __new__(self,first):
        return json.dumps({'first': first.get_html()})

#-------------------------------------------------------------
# EvaluateDiff : (Diff) --> (Expression)
#-------------------------------------------------------------

MathematicalIdentity(
        internal='EvaluateDiff',
        first='Diff',
        prettytext = 'Evaluate Derivative').save()

class EvaluateDiff(Identity):
    def __new__(self,first):
        first = parse_sage_exp(first._sage_())
        return json.dumps({'first': first.get_html()})

MathematicalIdentity(
        internal='EvaluateIntegral',
        first='Integral',
        prettytext = 'Evaluate Integral').save()

class EvaluateIntegral(Identity):
    def __new__(self,first):
        first = parse_sage_exp(first._sage_())
        return json.dumps({'first': first.get_html()})

MathematicalIdentity(
        internal='LengthTo_ly',
        first='Length',
        prettytext = '$$[ly]$$').save()

class LengthTo_ly(Identity):
    def __new__(self,first):
        first.convert_unit(Unit('ly'))
        return json.dumps({'first': first.get_html()})

MathematicalIdentity(
        internal='LengthTo_km',
        first='Length',
        prettytext = '$$[km]$$').save()

class LengthTo_km(Identity):
    def __new__(self,first):
        first.convert_unit(Unit('km'))
        return json.dumps({'first': first.get_html()})

MathematicalIdentity(
        internal='Momentum_Def1',
        first='Momentum',
        prettytext = '$$p=mv$$').save()

class Momentum_Def1(Identity):
    def __new__(self,first):
        first = Product(Mass(Base_Symbol('m')),Velocity(Base_Symbol('v')))
        return json.dumps({'first': first.get_html()})

