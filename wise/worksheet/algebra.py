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
    return tm

PlaceholderSubstitute.pretty = 'Substitute'

@Map( _( Term , Term ) >> _( Term ) )
def Replace( first, second ):
    return second

@Map( _( Definition , Equation ) >> _( Definition, Equation ) )
def Reduce( first, second ):
    rule = python_to_pure(first)
    print 'new_rule',python_to_pure(first)
    return first,pure_to_python(pure.reduce_with(rule,python_to_pure(second)))

mappings = iter_mappings(locals())

