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

from library_utils import *
from library_utils import _

from wise.worksheet.mathobjects import *

@Map( _( Numeric , Numeric ) >> _( Numeric ) )
def add(a,b):
    return Numeric(a.number+b.number)

add.pretty = 'Add'

@Map( _( Placeholder , Term ) >> _( Term ) )
def PlaceholderSubstitute( ph, tm ):
    return tm, 'pass'

PlaceholderSubstitute.pretty = 'Substitute'

@Map( _( Term , Term ) >> _( Term ) )
def Replace( first, second ):
    return second

@Map( _( Term ) >> _( Term ) )
def RefreshTerm( first ):
    return first

RefreshTerm.pretty = 'Refresh'

@Map( _( Equation ) >> _( Equation ) )
def RefreshEq( first ):
    return first

RefreshEq.pretty = 'Refresh'

@Map( _( Equation, Variable ) >> _( Equation ) )
def IntegrateEq( first, second ):
    dff = Differential(second)
    return Equation(Integral(first.lhs.lhs,dff),Integral(first.rhs.rhs,dff))

@Map( _( Definition , Equation ) >> _( None, Equation ) )
def ReduceEq( first, second ):
    rule = python_to_pure(first)
    print 'new_rule',python_to_pure(first)
    return 'pass' ,pure_to_python(pure.reduce_with(rule,python_to_pure(second)),first.idgen)

@Map( _( Definition , Term ) >> _( None, Term ) )
def ReduceTerm( first, second ):
    rule = python_to_pure(first)
    print 'new_rule',python_to_pure(first)
    return 'pass' ,pure_to_python(pure.reduce_with(rule,python_to_pure(second)),first.idgen)

@Map( _( Term ) >> _( Term ) )
def PlusZero( first ):
    return pure_to_python( pure.addzero( python_to_pure(first)) ,first.idgen)

@Map( _( Term ) >> _( Term ) )
def Simplify( first ):
    pfirst = python_to_pure(first)
    pfirst.refresh()
    print 'simplified',pure.simp(pfirst)
    return pure_to_python(pure.simp(pfirst), first.idgen)


mappings = iter_mappings(locals())

