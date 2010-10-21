from wise.library_utils import *
from wise.library_utils import _

import objects
from wise.worksheet.pure_wrap import i2p, env

Placeholder = objects.Placeholder
Term = objects.Term

@Map( _( Placeholder , Term ) >> _( Term ) )
def PlaceholderSubstitute( ph, tm ):
    return tm, 'pass'

PlaceholderSubstitute.pretty = 'Substitute'

@Map( _( Term , Term ) >> _( Term ) )
def CommandLine( old, cmd ):
    new = pure_to_python(env.eval(cmd))
    return new, 'pass'

@Map( _( Term ) >> _( Placeholder ) )
def Delete( first ):
    return Placeholder()

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
