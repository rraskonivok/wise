import translate
from pure_wrap import PureLevel, reduce_with_pure_rules
from worksheet.utils import hasharray

# A lookup table mapping previously run rules to their
# Cython equivelents to avoid the cost of translation
# for future use
rulecache = {}

def ReduceWithRules( rules, expr ):
    '''Reduce the given expression with a list of PureRules
    specified as an array of strings which are translated into
    Pure code.'''

    hsh = hasharray(rules)

    if hsh in rulecache:
        plevel = rulecache[hsh]
    else:
        print 'Building up new rule'
        plevel = PureLevel(rules)
        rulecache[hsh] = plevel
        print 'Rule cache size:', len(rulecache)

    pexpr = translate.python_to_pure(expr)
    pure_expr = reduce_with_pure_rules(plevel, pexpr)

    #debug(str(pexpr) + ' ----> ' + str(pure_expr))
    return translate.pure_to_python(pure_expr,expr.idgen)

def ReduceWithExternalRule( ref, expr ):
    '''Reduce the given expression with an external Pure symbol
    which corresponds to a set of rules defined in an external
    prelude'''

    pexpr = translate.python_to_pure(expr)
    pure_expr = ref(pexpr)

    #debug(str(pexpr) + ' ----> ' + str(pure_expr))
    return translate.pure_to_python(pure_expr,expr.idgen)
