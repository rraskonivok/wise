# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from logger import debug

from wise.library_utils import *
from wise.library_utils import _

#from wise.worksheet.mathobjects import *
#
#@Map( _( Placeholder , Term ) >> _( Term ) )
#def PlaceholderSubstitute( ph, tm ):
#    return tm, 'pass'
#
#PlaceholderSubstitute.pretty = 'Substitute'
#
#@Map( _( Term , Term ) >> _( Term ) )
#def Replace( first, second ):
#    return second
#
#@Map( _( Term ) >> _( Term ) )
#def RefreshTerm( first ):
#    return first
#
#RefreshTerm.pretty = 'Refresh'
#
#@Map( _( Equation ) >> _( Equation ) )
#def RefreshEq( first ):
#    return first
#
#RefreshEq.pretty = 'Refresh'
#
#@Map( _( Equation, Variable ) >> _( Equation ) )
#def IntegrateEq( first, second ):
#    dff = Differential(second)
#    return Equation(Integral(first.lhs.lhs,dff),Integral(first.rhs.rhs,dff))
#
#@Map( _( Definition , Equation ) >> _( None, Equation ) )
#def ReduceEq( rule, expr ):
#    rule = str(python_to_pure(rule))
#    hsh = hash(rule)
#
#    if hsh in rulecache:
#        plevel = rulecache[hsh]
#    else:
#        print 'Building up new rule'
#        plevel = pure.PureLevel([rule])
#        rulecache[hsh] = plevel
#        print 'Rule cache size:', len(rulecache)
#
#    pexpr = python_to_pure(expr)
#
#    pure_expr = pure.reduce_with_pure_rules(plevel, pexpr)
#
#    debug(str(pexpr) + ' ----> ' + str(pure_expr))
#    return 'pass',pure_to_python(pure_expr,expr.idgen)
#
#def ReduceWithRules( rules, expr ):
#    hsh = hasharray(rules)
#
#    if hsh in rulecache:
#        plevel = rulecache[hsh]
#    else:
#        print 'Building up new rule'
#        plevel = pure.PureLevel(rules)
#        rulecache[hsh] = plevel
#        print 'Rule cache size:', len(rulecache)
#
#    pexpr = python_to_pure(expr)
#
#    pure_expr = pure.reduce_with_pure_rules(plevel, pexpr)
#
#    debug(str(pexpr) + ' ----> ' + str(pure_expr))
#    return pure_to_python(pure_expr,expr.idgen)
#
#@Map( _( Definition , Term ) >> _( None, Term ) )
#def ReduceTerm( first, second ):
#    rule = python_to_pure(first)
#    print 'new_rule',python_to_pure(first)
#    return 'pass' ,pure_to_python(pure.reduce_with(rule,python_to_pure(second)),first.idgen)
#
#@Map( _( Term ) >> _( Term ) )
#def PlusZero( first ):
#    return pure_to_python( pure.addzero( python_to_pure(first)) ,first.idgen)
#
#@Map( _( Term ) >> _( Term ) )
#def Simplify( first ):
#    pfirst = python_to_pure(first)
#    pfirst.refresh()
#    print 'simplified',pure.simp(pfirst)
#    return pure_to_python(pure.simp(pfirst), first.idgen)
#
#
#mappings = iter_mappings(locals())

