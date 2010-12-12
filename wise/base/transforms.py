from wise.library_utils import *
from wise.library_utils import _

import objects
from wise.translators.pure_wrap import i2p, env

Placeholder = objects.Placeholder
Term = objects.Term

@Map( _( Placeholder , Term ) >> _( Term ) )
def PlaceholderSubstitute( ph, tm ):
    return tm, 'pass'

def GenFunc( func, term ):
    return 'pass', objects.FunctionAppl(func, Placeholder())

@Map( _( Term ) >> _( Term ) )
def Rebuild( term ):
    return term

@Map( _( Term ) >> _( Placeholder ) )
def Delete( first ):
    return Placeholder(),

def ReduceWithRules( rules, expr ):
    hsh = hasharray(rules)

    if hsh in rulecache:
        plevel = rulecache[hsh]
    else:
        print 'Building up new rule'
        plevel = pure.PureLevel(rules)
        rulecache[hsh] = plevel
        print 'Rule cache size:', len(rulecache)

    pexpr = python_to_pure(expr)

    pure_expr = pure.reduce_with_pure_rules(plevel, pexpr)

    #debug(str(pexpr) + ' ----> ' + str(pure_expr))
    return pure_to_python(pure_expr,expr.idgen)
